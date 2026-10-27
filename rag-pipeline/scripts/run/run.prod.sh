#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${PROJECT_ROOT}"
export ENVIRONMENT="production"

echo "Running cryptographic migration check before starting production application..."
bash "${PROJECT_ROOT}/scripts/migrate/migrate.sh"

echo "Starting Production RAG Pipeline server on ${HOST:-0.0.0.0}:${PORT:-8000}..."
exec python3 -m uvicorn src.main:app \
  --host "${HOST:-0.0.0.0}" \
  --port "${PORT:-8000}" \
  --workers "${WORKERS:-4}" \
  --no-access-log
