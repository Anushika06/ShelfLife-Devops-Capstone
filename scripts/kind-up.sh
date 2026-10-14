#!/usr/bin/env bash
# Create the local kind cluster and install: Traefik (Ingress controller),
# kube-prometheus-stack (Prometheus + Grafana) and the ShelfLife chart as a
# Helm CLI release in namespace "shelflife".
#
# Usage (repository root, Git Bash / Linux / macOS):
#   scripts/kind-up.sh --local                  build images locally and `kind load` them
#   scripts/kind-up.sh --ghcr <owner> <sha>     use the images CI pushed to GHCR
#
# Requires docker, kind, kubectl, helm. Safe to re-run (everything is an upgrade).
set -euo pipefail

CLUSTER=shelflife
TRAEFIK_CHART_VERSION=41.7.1
KPS_CHART_VERSION=92.3.1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mode="${1:-}"
case "$mode" in
  --local)
    image_args=(-f helm/shelflife/values-local-images.yaml)
    ;;
  --ghcr)
    owner="${2:?usage: --ghcr <github-owner> <git-sha>}"
    sha="${3:?usage: --ghcr <github-owner> <git-sha>}"
    owner="$(echo "$owner" | tr '[:upper:]' '[:lower:]')"
    image_args=(
      --set "backend.image.repository=ghcr.io/${owner}/shelflife-backend" --set "backend.image.tag=${sha}"
      --set "frontend.image.repository=ghcr.io/${owner}/shelflife-frontend" --set "frontend.image.tag=${sha}"
    )
    ;;
  *)
    echo "usage: $0 --local | --ghcr <github-owner> <git-sha>" >&2
    exit 2
    ;;
esac

step() { printf '\n==> %s\n' "$*"; }

step "kind cluster '${CLUSTER}'"
if kind get clusters | grep -qx "$CLUSTER"; then
  echo "already exists"
else
  kind create cluster --name "$CLUSTER" --config k8s/kind-config.yaml --wait 120s
fi
kubectl config use-context "kind-${CLUSTER}" >/dev/null

if [ "$mode" = "--local" ]; then
  step "build images and load them into kind"
  docker compose build backend frontend
  kind load docker-image shelflife-backend:local shelflife-frontend:local --name "$CLUSTER"
fi

step "Helm repositories"
helm repo add traefik https://traefik.github.io/charts >/dev/null 2>&1 || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

step "Traefik Ingress controller"
helm upgrade --install traefik traefik/traefik --version "$TRAEFIK_CHART_VERSION" \
  -n traefik --create-namespace -f k8s/ingress-controller/traefik-values-kind.yaml --wait --timeout 5m

step "Prometheus + Grafana (kube-prometheus-stack)"
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f - >/dev/null
if ! kubectl -n monitoring get secret grafana-admin >/dev/null 2>&1; then
  password="$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 20 || true)"
  kubectl -n monitoring create secret generic grafana-admin \
    --from-literal=admin-user=admin --from-literal=admin-password="$password" >/dev/null
  echo "created secret monitoring/grafana-admin with a random password (not written to disk)"
fi
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version "$KPS_CHART_VERSION" \
  -n monitoring -f monitoring/prometheus-values.yaml -f monitoring/grafana-values.yaml --wait --timeout 10m

step "ShelfLife namespace + Helm release"
kubectl apply -f k8s/namespace.yaml
helm upgrade --install shelflife ./helm/shelflife -n shelflife \
  -f helm/shelflife/values-kind.yaml "${image_args[@]}" --wait --timeout 6m
helm test shelflife -n shelflife --logs | tail -n 3

step "status"
kubectl get pods,svc,ingress -n shelflife
echo
echo "App via Ingress : http://shelflife.localtest.me:8088"
echo "Grafana         : http://grafana.localtest.me:8088   (user admin)"
echo "  admin password: kubectl -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d"
echo "Prometheus      : http://prometheus.localtest.me:8088/targets (serviceMonitor/shelflife/shelflife-backend)"
echo "Seed demo data  : scripts/seed-demo-data.sh http://shelflife.localtest.me:8088"
echo "Live traffic    : scripts/generate-traffic.sh http://shelflife.localtest.me:8088 180"
