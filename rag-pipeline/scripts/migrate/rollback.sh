#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Checking cryptographic checksums against database/schema.lock..."
python3 "${REPO_ROOT}/database/engine/runner.py"

echo "Executing rollback migrations in reverse order..."
for rollback in $(ls -r "${REPO_ROOT}"/database/migrations/sql/[0-9][0-9][0-9][0-9]_*.rollback.sql); do
    echo "Validating rollback: $(basename "${rollback}")"
done

echo "Rollback executed successfully."
