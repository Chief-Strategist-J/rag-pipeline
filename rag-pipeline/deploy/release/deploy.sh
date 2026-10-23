#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

kubectl apply -k "${DEPLOY_DIR}/k8s/overlays/${ENVIRONMENT}"
kubectl rollout status deployment/rag-pipeline -n "rag-${ENVIRONMENT}" --timeout=180s
