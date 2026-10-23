#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${HELM_DIR}/release"

mkdir -p "${OUTPUT_DIR}"

helm package "${HELM_DIR}/packaging" --destination "${OUTPUT_DIR}"
