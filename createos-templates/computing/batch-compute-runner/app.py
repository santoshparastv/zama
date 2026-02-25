"""
Batch Compute Runner — Run CPU-bound tasks via a simple API.
Use env vars for config; no secrets in code.
"""
import os
import uuid
import concurrent.futures
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# Config from environment (recommended for CreateOS / production)
WORKERS = int(os.environ.get("COMPUTE_WORKERS", "4"))
MAX_JOBS = int(os.environ.get("COMPUTE_MAX_JOBS", "100"))

app = FastAPI(title="Batch Compute Runner", version="1.0.0")
executor = concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS)
jobs: dict[str, dict] = {}


def run_task(payload: dict) -> dict:
    """CPU-bound work: simulate computation. Replace with your own logic."""
    n = payload.get("iterations", 1_000_000)
    total = 0
    for i in range(n):
        total += i % 37
    return {"result": total, "iterations": n, "computed_at": datetime.utcnow().isoformat()}


class JobRequest(BaseModel):
    iterations: Optional[int] = 1_000_000


class JobResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None
    created_at: str


@app.post("/jobs", response_model=JobResponse)
def submit_job(req: JobRequest):
    if len(jobs) >= MAX_JOBS:
        raise HTTPException(status_code=503, detail="Max jobs reached; try again later.")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "result": None,
        "created_at": datetime.utcnow().isoformat(),
        "future": None,
    }
    future = executor.submit(run_task, {"iterations": req.iterations or 1_000_000})
    jobs[job_id]["future"] = future
    return JobResponse(job_id=job_id, status="pending", result=None, created_at=jobs[job_id]["created_at"])


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    rec = jobs[job_id]
    future = rec.get("future")
    if future and future.done():
        try:
            rec["result"] = future.result()
            rec["status"] = "completed"
        except Exception as e:
            rec["status"] = "failed"
            rec["result"] = {"error": str(e)}
    elif future:
        rec["status"] = "running"
    return JobResponse(
        job_id=job_id,
        status=rec["status"],
        result=rec.get("result"),
        created_at=rec["created_at"],
    )


@app.get("/")
def root():
    return {"app": "Batch Compute Runner", "docs": "/docs", "health": "/health", "metrics": "/metrics"}


@app.get("/health")
def health():
    return {"status": "ok", "workers": WORKERS}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Prometheus-style metrics for platform scrapers."""
    pending = sum(1 for j in jobs.values() if j.get("status") == "pending")
    running = sum(1 for j in jobs.values() if j.get("status") == "running")
    completed = sum(1 for j in jobs.values() if j.get("status") == "completed")
    return "\n".join([
        "# HELP compute_jobs_total Total jobs by status",
        "# TYPE compute_jobs_total gauge",
        f"compute_jobs_total{{status=\"pending\"}} {pending}",
        f"compute_jobs_total{{status=\"running\"}} {running}",
        f"compute_jobs_total{{status=\"completed\"}} {completed}",
        f"compute_workers_config {{}} {WORKERS}",
        "",
    ])


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
