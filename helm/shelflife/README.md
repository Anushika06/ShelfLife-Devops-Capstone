# helm/shelflife — ShelfLife Helm chart

One chart deploys the whole application. It is used three ways: by the Helm CLI on kind
(`shelflife` namespace), by the CI smoke test, and by Argo CD (`shelflife-gitops` namespace).

| Template | Creates |
| --- | --- |
| `backend.yaml` | Backend Deployment (2 replicas) + ClusterIP Service on 8000; startup/liveness `/health`, readiness `/ready` |
| `frontend.yaml` | Frontend Deployment (2 replicas, Nginx on 8080) + ClusterIP Service on 80; probe `/healthz` |
| `postgres.yaml` | PostgreSQL 17 StatefulSet, Service and Secret (PVC when `postgres.persistence.enabled`) |
| `ingress.yaml` | Traefik Ingress: `/api` → backend, `/` → frontend |
| `pdb.yaml`, `hpa.yaml` | PodDisruptionBudgets; optional HPAs (off by default, need metrics-server) |
| `servicemonitor.yaml` | Prometheus scrape config for the backend `/metrics` |
| `grafana-dashboard.yaml` | ConfigMap with `dashboards/shelflife.json` for the Grafana sidecar |
| `tests/test-connection.yaml` | `helm test` pod that calls the services |

Backend and frontend containers run as non-root with a read-only root filesystem, dropped capabilities, no privilege
escalation and the `RuntimeDefault` seccomp profile. Image tags are required: the chart refuses to
render with an implicit `latest`.

| Values file | Use |
| --- | --- |
| `values.yaml` | Defaults (GHCR images, 2+2 replicas, 1 GiB Postgres PVC) |
| `values-kind.yaml` | Local kind cluster, host `shelflife.localtest.me`, dashboard on |
| `values-local-images.yaml` | Images built locally and loaded with `kind load` |
| `values-eks.yaml` | EKS (Postgres persistence off — no EBS CSI driver installed) |
| `values-gitops.yaml` | Argo CD release; the image SHA is rewritten by CI on every green `main` build |

The default database password `change-me-demo-only` is a demo placeholder; for anything real,
create a Secret (keys `username`, `password`) and set `postgres.auth.existingSecret`.

## Commands

```bash
kubectl apply -f k8s/namespace.yaml
helm lint helm/shelflife -f helm/shelflife/values-kind.yaml --set backend.image.tag=x --set frontend.image.tag=x
helm upgrade --install shelflife ./helm/shelflife -n shelflife -f helm/shelflife/values-kind.yaml \
  --set backend.image.tag=<git-sha> --set frontend.image.tag=<git-sha> --wait
helm test shelflife -n shelflife
kubectl get pods,svc,ingress -n shelflife
helm list -n shelflife
```

`scripts/kind-up.sh` does all of this (plus Traefik and monitoring) in one step.
