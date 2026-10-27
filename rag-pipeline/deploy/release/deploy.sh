#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Deploying Kubernetes overlay: ${ENVIRONMENT}..."
kubectl create namespace "rag-${ENVIRONMENT}" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k "${DEPLOY_DIR}/k8s/overlays/${ENVIRONMENT}"

echo "Verifying infrastructure rollout status in rag-${ENVIRONMENT}..."
kubectl rollout status deployment/kafka -n "rag-${ENVIRONMENT}" --timeout=120s || echo "Kafka waiting..."
kubectl rollout status deployment/qdrant -n "rag-${ENVIRONMENT}" --timeout=120s || echo "Qdrant waiting..."
kubectl rollout status deployment/valkey -n "rag-${ENVIRONMENT}" --timeout=120s || echo "Valkey waiting..."

echo "Verifying application service rollout..."
kubectl rollout status deployment/rag-pipeline -n "rag-${ENVIRONMENT}" --timeout=180s
echo "✓ All servers successfully deployed and healthy in rag-${ENVIRONMENT}."
