# Trivy image scanning

## What the pipeline does

The `images` job in `.github/workflows/ci-cd.yml` builds each image
(`ghcr.io/<owner>/shelflife-backend:<sha>` and `ghcr.io/<owner>/shelflife-frontend:<sha>`) and runs:

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 <image>:<sha>
```

- `--severity HIGH,CRITICAL` — only these two levels are reported.
- `--ignore-unfixed` — vulnerabilities that have no fixed version yet are not reported
  (you cannot remediate them by upgrading; they are re-checked on every build).
- `--exit-code 1` — any remaining finding makes the step, and therefore the pipeline, fail.
  The push to GHCR comes *after* the scan in the same job, so a vulnerable image is never published.

Trivy inspects the OS packages of the base image (Debian 13 for the backend, Alpine for
the frontend) and the language packages it finds in the image (Python packages in the
backend virtualenv and the system Python; the frontend image contains only static files
and Nginx).

## What happened during development (local scan, not CI evidence)

Scanned with Trivy 0.75.0 on the developer machine on 14 October 2026:

| Image | First scan | After fix |
|---|---|---|
| `shelflife-frontend:local` (nginx-unprivileged 1.31, Alpine 3.24) | 0 HIGH/CRITICAL | 0 |
| `shelflife-backend:local` (python:3.13-slim, Debian 13.7) | 4 HIGH (Python packages) | 0 |

The four backend findings were not in ShelfLife's own dependencies. They were libraries that
**pip vendors inside itself** (`pip/_vendor/urllib3` 2.7.0 — CVE-2026-97687, CVE-2026-97689;
`pip/_vendor/msgpack` 1.1.2 — GHSA-6v7p-g79w-8964; setuptools 70.3.0 metadata in pip's
`vendor.txt` — CVE-2025-47273), present both in the base image and in the virtualenv. The
application never runs pip at runtime, so the Dockerfile now uninstalls pip after the
dependencies are installed and removes `ensurepip` from the runtime stage. The re-scan
of the rebuilt image reported no HIGH/CRITICAL findings.

Example: CVE-2026-97689 is a denial-of-service in urllib3's chunked-response parser
(unbounded memory allocation). It would only matter if pip downloaded from a malicious
server inside the running container — which the app never does — but removing pip
removes the vulnerable code entirely instead of accepting the risk.

## Result in the CI pipeline (graded evidence)

GitHub Actions run #2 on `main`, commit `b728abc3da79747e436f33cf819aa1e97c21b40f`,
14 October 2026 — [run page](https://github.com/Anushika06/ShelfLife-Devops-Capstone/actions/runs/38564197363).

| Image | Trivy target | HIGH/CRITICAL (fixable) | Gate | Screenshot |
|---|---|---|---|---|
| `ghcr.io/anushika06/shelflife-frontend:b728abc…` | Alpine 3.24.2 OS packages | 0 (report summary: Vulnerabilities `0`) | passed, pushed | `demo/evidence/E07-trivy-scan-frontend.png` |
| `ghcr.io/anushika06/shelflife-backend:b728abc…` | OS packages + Python packages in `/opt/venv` | 0 (step exited 0 with `--exit-code 1`; the Python package rows in the screenshot all show `0`) | passed, pushed | `demo/evidence/E07-trivy-scan-backend.png` |

## Explanation

Trivy scanned the operating-system packages and the Python dependencies inside both container
images that the pipeline built for commit `b728abc`, before either image was pushed. It found no
HIGH or CRITICAL vulnerabilities that have a fixed version available, so the security gate passed
and both images were published to GHCR with the commit SHA as their tag. Vulnerabilities without a
fix are excluded by `--ignore-unfixed` and are re-checked on every build, because the Trivy
database is updated daily.

## If a future run fails

Open the Trivy step log, note the package, CVE and "Fixed Version", then upgrade that package (or
the base image tag) and push again. Only as a last resort, and with a written justification, add
the CVE ID to a `.trivyignore` file.

## Configuration scan (local, not part of the pipeline)

`trivy config` (Trivy 0.75.0, 15 October 2026) on the repository reported no HIGH/CRITICAL
misconfigurations in the Helm chart, Kubernetes manifests or Dockerfiles. It reported five in
`terraform/main.tf`, all known cost/demo trade-offs documented in the root README: public EKS API
endpoint open to `0.0.0.0/0` by default (restrict it with `cluster_endpoint_public_access_cidrs`),
no KMS envelope encryption for Kubernetes secrets, and public IPs on the two public subnets (needed
because there is no NAT gateway).
