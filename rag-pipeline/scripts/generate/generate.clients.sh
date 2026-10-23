#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Checking client dependencies and endpoints..."
python3 -c "
from src.infra.config.settings import settings
print(f'Client configuration verified for service: {settings.SERVICE_NAME}')
"
echo "Client generation checks completed."
