#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CLUSTER_NAME="${KIND_CLUSTER_NAME:-rag-cluster}"
ARGOCD_PORT="${ARGOCD_PORT:-8080}"

echo "========================================================"
echo "  RAG Pipeline Kubernetes & ArgoCD Lifecycle Runner     "
echo "========================================================"

# Edge Case 1: Check if Kubernetes cluster is reachable
ensure_cluster() {
  if kubectl cluster-info >/dev/null 2>&1; then
    echo "✓ Active Kubernetes cluster detected ($(kubectl config current-context))."
    return 0
  fi

  echo "! No active cluster context detected."

  # Check if kind cluster already exists but is stopped or not targeted
  if command -v kind >/dev/null 2>&1; then
    EXISTING_CLUSTERS=$(kind get clusters 2>/dev/null || true)
    if echo "${EXISTING_CLUSTERS}" | grep -q "^${CLUSTER_NAME}$"; then
      echo "✓ Kind cluster '${CLUSTER_NAME}' already exists. Pointing kubectl context..."
      kubectl config use-context "kind-${CLUSTER_NAME}"
    else
      echo "+ Creating Kind cluster '${CLUSTER_NAME}'..."
      kind create cluster --name "${CLUSTER_NAME}"
    fi
  elif command -v minikube >/dev/null 2>&1; then
    echo "+ Starting minikube cluster..."
    minikube start
  else
    echo "ERROR: No Kubernetes cluster reachable and neither 'kind' nor 'minikube' is available." >&2
    exit 1
  fi
}

# Edge Case 1.5: Ensure metrics-server is installed for HPA and kubectl top
ensure_metrics_server() {
  echo "--- Checking Metrics Server ---"
  if ! kubectl get deployment metrics-server -n kube-system >/dev/null 2>&1; then
    echo "+ Installing metrics-server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
  fi
}

# Edge Case 2: Ensure ArgoCD is installed and running
ensure_argocd() {
  echo "--- Checking ArgoCD Namespace & Controller ---"
  if ! kubectl get namespace argocd >/dev/null 2>&1; then
    echo "+ Creating 'argocd' namespace..."
    kubectl create namespace argocd
  fi

  if ! kubectl get deployment argocd-server -n argocd >/dev/null 2>&1; then
    echo "+ Installing ArgoCD core manifests..."
    kubectl apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    kubectl -n argocd patch configmap argocd-cmd-params-cm --type merge -p '{"data":{"server.insecure":"true"}}'
  fi

  echo "Waiting for ArgoCD server deployment to be ready..."
  kubectl rollout status deployment/argocd-server -n argocd --timeout=300s
}

# Edge Case 3: Register ArgoCD Project and Applications
register_argocd_apps() {
  echo "--- Registering ArgoCD Project and ApplicationSet ---"
  if [ -f "${DEPLOY_DIR}/argocd/project.yaml" ]; then
    kubectl apply -f "${DEPLOY_DIR}/argocd/project.yaml"
  fi

  if [ -f "${DEPLOY_DIR}/argocd/applicationset.yaml" ]; then
    kubectl apply -f "${DEPLOY_DIR}/argocd/applicationset.yaml"
  fi
}

# Edge Case 4: Retrieve admin password and provide port-forwarding URL
expose_argocd() {
  echo "--- ArgoCD Credentials & Access ---"
  ADMIN_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 -d || echo "")

  echo ""
  echo "========================================================"
  echo "  ArgoCD Access Details:"
  echo "  URL:      http://localhost:${ARGOCD_PORT} (or https://localhost:${ARGOCD_PORT})"
  echo "  Username: admin"
  if [ -n "${ADMIN_PASSWORD}" ]; then
    echo "  Password: ${ADMIN_PASSWORD}"
  else
    echo "  Password: (Already modified or retrieve using: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
  fi
  echo "========================================================"
  echo ""

  # Check if port-forward is already running on port
  if lsof -i ":${ARGOCD_PORT}" >/dev/null 2>&1; then
    echo "✓ Port ${ARGOCD_PORT} is already in use (ArgoCD or port-forward active)."
  else
    echo "Starting ArgoCD port-forward in background on port ${ARGOCD_PORT}..."
    nohup kubectl port-forward svc/argocd-server -n argocd "${ARGOCD_PORT}:80" >/dev/null 2>&1 &
    sleep 2
    echo "✓ ArgoCD UI live at: http://localhost:${ARGOCD_PORT}"
  fi
}

main() {
  ensure_cluster
  ensure_metrics_server
  ensure_argocd
  register_argocd_apps
  expose_argocd
}

main "$@"
