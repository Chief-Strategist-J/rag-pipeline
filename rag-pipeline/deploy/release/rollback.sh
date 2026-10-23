#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-prod}"

kubectl rollout undo deployment/rag-pipeline -n "rag-${ENVIRONMENT}"
kubectl rollout status deployment/rag-pipeline -n "rag-${ENVIRONMENT}" --timeout=180s
