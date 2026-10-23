#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RELEASE_DIR="${HELM_DIR}/release"
REGISTRY_URL="${HELM_REGISTRY_URL:-oci://us-central1-docker.pkg.dev/rag-prod-project/rag-repo-prod/charts}"

for chart_package in "${RELEASE_DIR}"/*.tgz; do
  if [ -f "${chart_package}" ]; then
    helm push "${chart_package}" "${REGISTRY_URL}"
  fi
done
