# CPU Pipeline

A **Computing** template for running multi-step CPU pipelines via a simple API. Submit a pipeline (number of steps + work per step), get results immediately. Suited for CreateOS one-click deploy.

## Features

- REST API: POST to run a pipeline, GET to fetch result
- Configurable max steps and work per step via environment variables
- No hardcoded secrets; use env vars for credentials and tuning
- One-click run script for local or CreateOS

## Setup

### One-click run

```bash
chmod +x run.sh
./run.sh
```

Or manually:

```bash
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Environment variables

| Variable | Description | Default |
|----------|-------------|--------|
| `PORT` | HTTP port | `8000` |
| `PIPELINE_MAX_STEPS` | Maximum steps per pipeline | `10` |
| `PIPELINE_DEFAULT_STEPS` | Default steps when not specified | `3` |

## Demo

Quick run (start server with `./run.sh`, then in another terminal):

```bash
curl -X POST http://localhost:8000/pipelines -H "Content-Type: application/json" -d '{"steps": 3, "work_per_step": 50000}'
```

Response includes `pipeline_id` and `result` in one request. Optional: add a short demo GIF (e.g. `demo.gif`) to showcase in the marketplace.

## API examples

### Run a pipeline

```bash
curl -X POST http://localhost:8000/pipelines \
  -H "Content-Type: application/json" \
  -d '{"steps": 3, "work_per_step": 50000}'
```

Response: `{"pipeline_id":"...", "status":"completed", "result":[...], "error":null, "created_at":"..."}`

### Get pipeline result

```bash
curl http://localhost:8000/pipelines/<pipeline_id>
```

### Health check

```bash
curl http://localhost:8000/health
```

## Customizing pipeline steps

Edit `app.py`: change `run_step(step_id, input_data)` to implement your own logic (e.g. parse → transform → aggregate). Keep secrets and config in environment variables.

## License

MIT — see [LICENSE](LICENSE).
