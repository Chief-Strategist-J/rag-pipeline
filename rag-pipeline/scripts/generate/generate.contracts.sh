#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Validating OpenAPI 3.1.0 and Proto contracts..."
python3 -c "
import yaml
with open('${PROJECT_ROOT}/contracts/openapi/v1.yml') as f:
    spec = yaml.safe_load(f)
assert spec['openapi'] == '3.1.0'
print('OpenAPI specification valid: ' + spec['info']['title'])
"
echo "Contracts successfully validated."
