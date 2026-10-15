# argocd/ — GitOps with Argo CD

`application.yaml` registers one Argo CD `Application` named `shelflife`:

- **Source:** this repository, branch `main`, path `helm/shelflife`, values file `values-gitops.yaml`
- **Destination:** namespace `shelflife-gitops` in the same cluster (created if missing)
- **Sync policy:** automated, with `prune` (resources deleted from Git are deleted from the
  cluster) and `selfHeal` (manual `kubectl` changes are reverted to what Git says)

The file itself is outside the synced path, so it is applied once by hand (or by
`scripts/argocd-up.sh`).

## How a release reaches the cluster

1. A push to `main` runs `.github/workflows/ci-cd.yml`.
2. Tests, Trivy and the kind smoke test pass; images are pushed as `:<git-sha>`.
3. The `gitops-promote` job writes that SHA into `helm/shelflife/values-gitops.yaml` and commits
   it as `chore(gitops): promote images <sha> ... [skip ci]`.
4. Argo CD sees the new commit and rolls out the new images in `shelflife-gitops`.

The Helm CLI release (`shelflife` namespace) and the Argo CD release are kept separate on purpose.

## Prerequisites

A running cluster (e.g. from `scripts/kind-up.sh`), `kubectl`, at least one green CI run on
`main`, and GHCR packages that are public (or an image pull secret).

## Commands

```bash
scripts/argocd-up.sh                                  # installs Argo CD v3.5.5 and applies application.yaml
kubectl -n argocd get applications
kubectl -n argocd port-forward svc/argocd-server 8443:443    # https://localhost:8443, user admin
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d; echo           # do not show this on screen

# optional self-heal demo
kubectl -n shelflife-gitops scale deploy/shelflife-frontend --replicas=1
kubectl -n shelflife-gitops get deploy shelflife-frontend -w   # Argo CD restores 2 replicas
```

App URL on kind: http://shelflife-gitops.localtest.me:8088. Evidence:
`demo/evidence/E17-argocd-synced.png` (Healthy, Synced to `18a0823`).

If you fork the repository, run `scripts/set-github-repo.sh <owner> <repo>` to update `repoURL`.
