"""
CPU Pipeline — Run a multi-step compute pipeline via API.
Each step is configurable; use env vars for secrets and tuning.
"""
import os
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# Config from environment
PIPELINE_MAX_STEPS = int(os.environ.get("PIPELINE_MAX_STEPS", "10"))
DEFAULT_STEPS = int(os.environ.get("PIPELINE_DEFAULT_STEPS", "3"))

app = FastAPI(title="CPU Pipeline", version="1.0.0")
pipelines: dict[str, dict] = {}


def run_step(step_id: int, input_data: dict) -> dict:
    """Simulate one pipeline step (e.g. transform, aggregate). Replace with your logic."""
    n = input_data.get("work", 100_000)
    acc = 0
    for i in range(n):
        acc += (step_id + 1) * (i % 31)
    return {
        "step": step_id,
        "output": acc,
        "at": datetime.utcnow().isoformat(),
    }


def run_pipeline_sync(num_steps: int, work_per_step: int) -> list[dict]:
    """Run steps sequentially. For parallel steps, use threading/process pool."""
    result = []
    data = {"work": work_per_step}
    for s in range(num_steps):
        data = run_step(s, data)
        result.append(data)
        data = {"work": work_per_step, "prev": data}
    return result


class PipelineRequest(BaseModel):
    steps: Optional[int] = 3
    work_per_step: Optional[int] = 100_000


class PipelineResponse(BaseModel):
    pipeline_id: str
    status: str
    result: Optional[list[dict]] = None
    error: Optional[str] = None
    created_at: str


@app.post("/pipelines", response_model=PipelineResponse)
def start_pipeline(req: PipelineRequest):
    steps = min(req.steps or DEFAULT_STEPS, PIPELINE_MAX_STEPS)
    work = req.work_per_step or 100_000
    pipeline_id = str(uuid.uuid4())
    try:
        result = run_pipeline_sync(steps, work)
        pipelines[pipeline_id] = {
            "status": "completed",
            "result": result,
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        pipelines[pipeline_id] = {
            "status": "failed",
            "result": None,
            "error": str(e),
            "created_at": datetime.utcnow().isoformat(),
        }
    rec = pipelines[pipeline_id]
    return PipelineResponse(
        pipeline_id=pipeline_id,
        status=rec["status"],
        result=rec.get("result"),
        error=rec.get("error"),
        created_at=rec["created_at"],
    )


@app.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: str):
    if pipeline_id not in pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    rec = pipelines[pipeline_id]
    return PipelineResponse(
        pipeline_id=pipeline_id,
        status=rec["status"],
        result=rec.get("result"),
        error=rec.get("error"),
        created_at=rec["created_at"],
    )


@app.get("/")
def root():
    return {"app": "CPU Pipeline", "docs": "/docs", "health": "/health", "metrics": "/metrics"}


@app.get("/health")
def health():
    return {"status": "ok", "max_steps": PIPELINE_MAX_STEPS}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Prometheus-style metrics for platform scrapers."""
    total = len(pipelines)
    completed = sum(1 for p in pipelines.values() if p.get("status") == "completed")
    failed = sum(1 for p in pipelines.values() if p.get("status") == "failed")
    return "\n".join([
        "# HELP pipeline_runs_total Total pipeline runs",
        "# TYPE pipeline_runs_total gauge",
        f"pipeline_runs_total {{}} {total}",
        "# HELP pipeline_runs_completed Completed pipeline runs",
        "# TYPE pipeline_runs_completed gauge",
        f"pipeline_runs_completed {{}} {completed}",
        "# HELP pipeline_runs_failed Failed pipeline runs",
        "# TYPE pipeline_runs_failed gauge",
        f"pipeline_runs_failed {{}} {failed}",
        f"pipeline_max_steps_config {{}} {PIPELINE_MAX_STEPS}",
        "",
    ])


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
