# Batch Compute Runner

A minimal **Computing** template for running CPU-bound batch jobs via a simple API. Submit jobs, poll for completion, get results. Suitable for CreateOS one-click deploy.

## Features

- REST API: submit jobs and check status/result
- Configurable workers and job limit via environment variables
- No hardcoded secrets; use env vars for any credentials
- One-click run script for local or CreateOS deploy

## Setup

### Requirements

- Python 3.10+
- `pip`

### Install and run (one-click)

```bash
chmod +x run.sh
./run.sh
```

Or manually:

```bash
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Deploy on CreateOS / NodeOps

- **Root directory** (if the platform asks): set to the folder that contains `app.py` (e.g. `batch-compute-runner` when the zip has that subfolder). Otherwise the app will fail with "No module named 'app'".
- **Start command** — use **one** of these (FastAPI is ASGI; do not use plain `gunicorn app:app`):
  - **Uvicorn (recommended):** `uvicorn app:app --host 0.0.0.0 --port $PORT`
  - **Gunicorn + Uvicorn worker** (if the platform uses Gunicorn): `gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

## Environment variables

| Variable | Description | Default |
|----------|-------------|--------|
| `PORT` | HTTP port | `8000` |
| `COMPUTE_WORKERS` | Number of worker processes | `4` |
| `COMPUTE_MAX_JOBS` | Max concurrent jobs | `100` |

## Demo

Quick run (start server with `./run.sh`, then in another terminal):

```bash
# Submit a job and get job_id from response, then:
curl -X POST http://localhost:8000/jobs -H "Content-Type: application/json" -d '{"iterations": 100000}'
curl http://localhost:8000/jobs/<job_id>
```

Optional: add a short screen recording or GIF to this repo (e.g. `demo.gif`) and link it here to showcase the template in the marketplace.

## API examples

### Submit a job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"iterations": 500000}'
```

Response: `{"job_id":"...", "status":"pending", "result":null, "created_at":"..."}`

### Get job status and result

```bash
curl http://localhost:8000/jobs/<job_id>
```

Response when completed: `{"job_id":"...", "status":"completed", "result":{"result":..., "iterations":500000, "computed_at":"..."}, "created_at":"..."}`

### Health check

```bash
curl http://localhost:8000/health
```

## Customizing the compute logic

Edit `app.py` and replace the body of `run_task(payload)` with your own CPU-bound work. Keep secrets and config in environment variables.

## License

MIT — see [LICENSE](LICENSE).
