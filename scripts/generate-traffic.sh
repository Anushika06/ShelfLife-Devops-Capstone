#!/usr/bin/env bash
# Send steady API traffic so Prometheus/Grafana panels have live data to show.
# Usage: scripts/generate-traffic.sh [BASE_URL] [SECONDS]
#   default BASE_URL http://localhost:3000, default duration 120 s.
set -euo pipefail
BASE_URL="${1:-http://localhost:3000}"
DURATION="${2:-120}"
end=$(( $(date +%s) + DURATION ))
count=0
echo "sending traffic to $BASE_URL for ${DURATION}s (Ctrl+C to stop)"
while [ "$(date +%s)" -lt "$end" ]; do
  curl -fsS -o /dev/null "$BASE_URL/api/items" || true
  curl -fsS -o /dev/null "$BASE_URL/api/summary" || true
  curl -fsS -o /dev/null "$BASE_URL/api/items?status=expiring" || true
  curl -sS  -o /dev/null "$BASE_URL/api/items/999999" || true   # deliberate 404s for the error panel
  count=$((count + 4))
  sleep 0.5
done
echo "sent $count requests"
