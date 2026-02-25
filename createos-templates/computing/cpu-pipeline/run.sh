#!/usr/bin/env bash
# One-click run script for CPU Pipeline (CreateOS / local)
set -e
cd "$(dirname "$0")"

if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
  . venv/bin/activate
fi

pip install -q -r requirements.txt
echo "Starting CPU Pipeline on port ${PORT:-8000}..."
exec python -m uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
