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

## Your 2–3 sentence explanation (write after the real CI run)

Replace this with what the **pipeline run** shows (the result can differ from the local
scan because the Trivy vulnerability database changes daily):

> _Example if the run is clean:_ Trivy scanned the OS packages and Python/Node
> dependencies inside both container images built by the pipeline for commit `<sha>`.
> It found no HIGH or CRITICAL vulnerabilities that have a fix available, so the security
> gate passed and the images were pushed to GHCR. Unfixed vulnerabilities are excluded and
> re-checked on every build.

If a future run fails, open the Trivy step log, note the package, CVE and "Fixed Version",
then upgrade that package (or the base image tag) and push again. Only as a last resort,
and with a written justification, add the CVE ID to a `.trivyignore` file.
