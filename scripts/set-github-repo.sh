#!/usr/bin/env bash
# Replace the GitHub placeholders in tracked config files with your repository.
# Usage: scripts/set-github-repo.sh <github-owner> <repo-name>
set -euo pipefail

owner="${1:?usage: $0 <github-owner> <repo-name>}"
repo="${2:?usage: $0 <github-owner> <repo-name>}"
lower_owner="$(echo "$owner" | tr '[:upper:]' '[:lower:]')" # GHCR image paths must be lowercase
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

files=(argocd/application.yaml helm/shelflife/values.yaml helm/shelflife/values-gitops.yaml README.md)
for f in "${files[@]}"; do
  sed -i.bak \
    -e "s#ghcr.io/YOUR_GITHUB_USERNAME/#ghcr.io/${lower_owner}/#g" \
    -e "s#YOUR_GITHUB_USERNAME#${owner}#g" \
    -e "s#YOUR_REPO_NAME#${repo}#g" "$f"
  rm -f "$f.bak"
  echo "updated $f"
done

if grep -nE "YOUR_GITHUB_USERNAME|YOUR_REPO_NAME" "${files[@]}"; then
  echo "some placeholders remain (see above)" >&2
else
  echo "no placeholders left in: ${files[*]}"
fi
