#!/usr/bin/env bash
# Delete the local kind cluster (all demo data inside it is removed).
set -euo pipefail
kind delete cluster --name shelflife
