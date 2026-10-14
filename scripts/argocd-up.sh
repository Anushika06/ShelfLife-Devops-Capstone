#!/usr/bin/env bash
# Install Argo CD (pinned version) into the current kubectl context and register
# the ShelfLife Application. Run after scripts/kind-up.sh, and after CI on main has
# pushed images and committed their SHA into helm/shelflife/values-gitops.yaml.
set -euo pipefail

ARGOCD_VERSION=v3.5.5
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if grep -qE "YOUR_GITHUB_USERNAME|YOUR_REPO_NAME" argocd/application.yaml; then
  echo "argocd/application.yaml still contains placeholders." >&2
  echo "Run: scripts/set-github-repo.sh <github-owner> <repo-name>, commit and push, then retry." >&2
  exit 1
fi

kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -n argocd --server-side --force-conflicts \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml" >/dev/null
echo "waiting for Argo CD..."
kubectl -n argocd rollout status deploy/argocd-server --timeout=5m
kubectl -n argocd rollout status deploy/argocd-repo-server --timeout=5m
kubectl -n argocd rollout status statefulset/argocd-application-controller --timeout=5m

kubectl apply -f argocd/application.yaml
kubectl -n argocd get applications

echo
echo "Argo CD UI : kubectl -n argocd port-forward svc/argocd-server 8443:443  -> https://localhost:8443"
echo "  user admin, password:"
echo "  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo "GitOps app : http://shelflife-gitops.localtest.me:8088"
