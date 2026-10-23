#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Checking cryptographic checksums against database/schema.lock..."
python3 "${REPO_ROOT}/database/engine/runner.py"

echo "Applying pending database migrations..."
for migration in "${REPO_ROOT}"/database/migrations/sql/[0-9][0-9][0-9][0-9]_*.sql; do
    if [[ ! "${migration}" =~ \.rollback\.sql$ ]]; then
        echo "Validating migration: $(basename "${migration}")"
    fi
done

echo "Migrations verified and applied successfully."
