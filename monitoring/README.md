# monitoring/ — Prometheus and Grafana

Helm values for **kube-prometheus-stack** (chart `92.3.1`), installed as release `monitoring`
in namespace `monitoring`.

| File | What it configures |
| --- | --- |
| `prometheus-values.yaml` | Prometheus selects ServiceMonitors from every namespace, 2-day retention, Traefik Ingress `prometheus.localtest.me`, control-plane scrape targets that kind/EKS do not expose are disabled |
| `grafana-values.yaml` | Admin credentials from the pre-created Secret `grafana-admin`, dashboard sidecar enabled, Traefik Ingress `grafana.localtest.me` |

The application side lives in the Helm chart:

- `helm/shelflife/templates/servicemonitor.yaml` — tells Prometheus to scrape the backend's `/metrics`
- `helm/shelflife/templates/grafana-dashboard.yaml` + `dashboards/shelflife.json` — the
  **ShelfLife API** dashboard, picked up automatically by the Grafana sidecar

Metrics exposed by the backend: `http_requests_total`, `http_request_duration_seconds`,
`shelflife_items_created_total`, `shelflife_items_consumed_total`, `shelflife_items_deleted_total`,
`shelflife_pantry_items{status=...}`.

## Prerequisites

A cluster with the Traefik Ingress controller (`scripts/kind-up.sh` installs everything) and Helm 4.

## Commands

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
kubectl create namespace monitoring
kubectl -n monitoring create secret generic grafana-admin \
  --from-literal=admin-user=admin --from-literal=admin-password='<choose-a-password>'
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.3.1 \
  -n monitoring -f monitoring/prometheus-values.yaml -f monitoring/grafana-values.yaml --wait --timeout 10m

# access (Ingress on kind, or port-forward)
#   http://prometheus.localtest.me:8088/targets   http://grafana.localtest.me:8088
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
kubectl -n monitoring port-forward svc/monitoring-grafana 3001:80

scripts/generate-traffic.sh http://shelflife.localtest.me:8088 180   # make the panels move
```

Evidence: `demo/evidence/E18-metrics-endpoint.png`, `E19-prometheus-targets-up.png`
(both backend ServiceMonitors 2/2 UP), `E20-grafana-dashboard.png`.
