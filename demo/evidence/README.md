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
| `E05-commit-history.png` | `git log --oneline`: 17 commits with conventional messages | M3 |
| `E06-github-actions-green.png` | Actions run #5 on `main` (commit `ff5e07d`): all 7 jobs green, 3 m 30 s, 6 artifacts | M5 |
| `E07-trivy-scan-backend.png` | Backend Trivy step ("fail on HIGH/CRITICAL"): Python packages in `/opt/venv` all `0` | M6 |
| `E07-trivy-scan-frontend.png` | Frontend Trivy step: image `…/shelflife-frontend:b728abc…` (Alpine 3.24.2), 0 vulnerabilities | M6 |
| `E08-ghcr-packages-backend.png` | GHCR `shelflife-backend`: tags are full commit SHAs (`b728abc…`, `5f64d0b…`) | M5 |
| `E08-ghcr-packages-frontend.png` | GHCR `shelflife-frontend`: same SHA tags | M5 |
| `E09-terraform-plan.png` | `terraform plan`: 16 to add, 0 to change, 0 to destroy; outputs for `ap-south-1` | M7 |
| `E09-terraform-apply.png` | `terraform apply` (second run): EKS cluster and node group created, 16 added, outputs; VPC `vpc-02fd16843a6086a5c` | M7 |
| `E10-aws-vpc.png` | AWS Console, Mumbai: `shelflife-vpc` (`vpc-0dae89e7d0878947b`), 10.42.0.0/16, Available, 2 subnets | M7 |
| `E10-aws-subnets.png` | `shelflife-public-ap-south-1a` (10.42.0.0/20) and `-1b` (10.42.16.0/20) | M7 |
| `E11-aws-eks.png` | EKS node group `shelflife-nodes` Active: Kubernetes 1.36, AL2023, t3.small, 2 nodes | M7 |
| `E11-aws-eks-nodes.png` | `kubectl get nodes -o wide` on EKS: 2 nodes Ready (v1.36.4-eks) | M7 |
| `E12-terraform-destroy.png` | `terraform destroy` (first run): "Destroy complete! Resources: 16 destroyed."; VPC `vpc-0dae89e7d0878947b` | M7 |
| `E12-aws-leftovers-check.png` | `scripts/aws-check-leftovers.sh ap-south-1`: no leftovers | M7 |
| `E13-kubernetes-resources.png` | kind, `kubectl get pods,svc,ingress -n shelflife`: 2 backend + 2 frontend + postgres Running, ClusterIP services, Traefik Ingress | M8 |
| `E14-kubernetes-services.png` | `kubectl get svc -n shelflife`: three ClusterIP services | M8 |
| `E15-helm-release.png` | `helm list -n shelflife`: release `shelflife` revision 1 deployed (chart 0.1.0) | M8 |
| `E16-app-via-ingress.png` | App through the Ingress at `http://shelflife.localtest.me:8088` | M8 |
| `E17-argocd-synced.png` | Argo CD v3.5.5: app `shelflife` Healthy, Synced to `main` (18a0823), auto sync on, resource tree | Video (GitOps) |
| `E18-metrics-endpoint.png` | `curl …/metrics` filtered to `http_requests_total` and `shelflife_*` metrics | M9 |
| `E19-prometheus-targets-up.png` | Prometheus Target health: `serviceMonitor/shelflife/shelflife-backend/0` and `…shelflife-gitops…` both 2/2 UP | M9 |
| `E20-grafana-dashboard.png` | Grafana "ShelfLife API": 4 pods up, 7.32 req/s, p95 95.2 ms, error ratio 25.0%, endpoint/status/latency/pantry panels | M9 |

## Notes for reviewers

- Kubernetes, Argo CD, Prometheus and Grafana screenshots come from the local **kind** cluster.
  The EKS cluster was provisioned and destroyed for the Terraform evidence only.
- The EKS run used `t3.small` nodes via the git-ignored `terraform.tfvars`; the code default is `t3.medium`.
- **Terraform apply/destroy: two separate runs.** I ran `terraform apply` and `terraform destroy` twice
  in total. I forgot to capture the apply terminal output during the first run (the one that produced
  E10–E11 and E12). I therefore ran Terraform a second time and captured `E09-terraform-apply.png`
  during that second apply. As a result, the VPC ID visible in `E09-terraform-apply.png`
  (`vpc-02fd16843a6086a5c`) differs from the VPC ID in `E10-aws-vpc.png` and
  `E12-terraform-destroy.png` (`vpc-0dae89e7d0878947b`), which belong to the first run.
  Both runs produced identical infrastructure (16 resources added, 16 destroyed); no screenshots
  have been altered or fabricated.
- The Grafana dashboard (E20) was captured during a traffic-generation run:
  `scripts/generate-traffic.sh` was active, which explains the elevated request rate (7.32 req/s)
  and the non-zero error ratio (25.0%) caused by deliberate 404 requests to test the error panel.
