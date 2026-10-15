# Evidence

Real screenshots captured by me while running the project on 14–15 October 2026.
Nothing here is generated or edited, apart from cropping by the screenshot tool. The slide deck
(`../presentation.pptx`, `../slides.pdf`) uses copies of these images in which the AWS account ID
is masked; the originals below are unchanged.

| File | What it shows | Rubric |
|---|---|---|
| `E01-app-browser.png` | ShelfLife at `http://localhost:3000` (Docker Compose): summary counts, "Use these first" shelf, inventory | M1, M4 |
| `E02-docker-compose-up.png` | `docker compose up --build`: both images built, postgres/backend Healthy, frontend Started; `docker ps` shows all three healthy | M4 |
| `E03-github-repo-codebase.png` | GitHub repository page: folders, README and the passing "ShelfLife CI/CD" badge | M3, M10 |
| `E04-pytest.png` | `pytest -v`: 17 collected, 17 passed | M2 |
| `E05-commit-history.png` | `git log --oneline`: 17 commits with conventional messages (taken before the evidence commit) | M3 |
| `E06-github-actions-green.png` | Actions run #2 on `main` (commit `b728abc`): all 7 jobs green, 4 m 2 s, 6 artifacts | M5 |
| `E07-trivy-scan-backend.png` | Backend Trivy step ("fail on HIGH/CRITICAL"): Python packages in `/opt/venv` all `0` | M6 |
| `E07-trivy-scan-frontend.png` | Frontend Trivy step: image `…/shelflife-frontend:b728abc…` (Alpine 3.24.2), 0 vulnerabilities | M6 |
| `E08-ghcr-packages-backend.png` | GHCR `shelflife-backend`: tags are full commit SHAs (`b728abc…`, `5f64d0b…`) | M5 |
| `E08-ghcr-packages-frontend.png` | GHCR `shelflife-frontend`: same SHA tags | M5 |
| `E09-terraform-plan.png` | `terraform plan`: 16 to add, 0 to change, 0 to destroy; outputs for `ap-south-1` | M7 |
| `E09-terraform-apply.png` | `terraform apply`: EKS cluster and node group created, 16 added, outputs | M7 |
| `E10-aws-vpc.png` | AWS Console, Mumbai: `shelflife-vpc`, 10.42.0.0/16, Available, 2 subnets | M7 |
| `E10-aws-subnets.png` | `shelflife-public-ap-south-1a` (10.42.0.0/20) and `-1b` (10.42.16.0/20) | M7 |
| `E11-aws-eks.png` | EKS node group `shelflife-nodes` Active: Kubernetes 1.36, AL2023, t3.small, 2 nodes | M7 |
| `E11-aws-eks-nodes.png` | `kubectl get nodes -o wide` on EKS: 2 nodes Ready (v1.36.4-eks) | M7 |
| `E12-terraform-destroy.png` | `terraform destroy`: "Destroy complete! Resources: 16 destroyed." | M7 |
| `E12-aws-leftovers-check.png` | `scripts/aws-check-leftovers.sh ap-south-1`: no leftovers | M7 |
| `E13-kubernetes-resources.png` | kind, `kubectl get pods,svc,ingress -n shelflife`: 2 backend + 2 frontend + postgres Running, ClusterIP services, Traefik Ingress | M8 |
| `E14-kubernetes-services.png` | `kubectl get svc -n shelflife`: three ClusterIP services | M8 |
| `E15-helm-release.png` | `helm list -n shelflife`: release `shelflife` revision 1 deployed (chart 0.1.0) | M8 |
| `E16-app-via-ingress.png` | App through the Ingress at `http://shelflife.localtest.me:8088` | M8 |
| `E17-argocd-synced.png` | Argo CD v3.5.5: app `shelflife` Healthy, Synced to `main` (18a0823), auto sync on, resource tree | Video (GitOps) |
| `E18-metrics-endpoint.png` | `curl …/metrics` filtered to `http_requests_total` and `shelflife_*` metrics | M9 |
| `E19-prometheus-targets-up.png` | Prometheus Target health: `serviceMonitor/shelflife/shelflife-backend/0` and `…shelflife-gitops…` both 2/2 UP | M9 |
| `E20-grafana-dashboard.png` | Grafana "ShelfLife API": 2 pods up, 0.199 req/s, p95 99.7 ms, endpoint/status/latency/pantry panels | M9 |

## Notes for reviewers

- Kubernetes, Argo CD, Prometheus and Grafana screenshots come from the local **kind** cluster.
  The EKS cluster was provisioned and destroyed for the Terraform evidence only.
- The EKS run used `t3.small` nodes via the git-ignored `terraform.tfvars`; the code default is `t3.medium`.
- The Grafana "Error ratio" panel shows *No data* because no 4xx/5xx responses had been recorded
  in that 30-minute window.
