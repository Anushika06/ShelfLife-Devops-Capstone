#!/usr/bin/env bash
# Add a realistic set of pantry items through the public API (not the database),
# so the demo shows data flowing frontend/API -> PostgreSQL.
# Usage: scripts/seed-demo-data.sh [BASE_URL]     default: http://localhost:3000
set -euo pipefail
BASE_URL="${1:-http://localhost:3000}"

day() {  # ISO date N days from today (GNU date on Linux/Git Bash, BSD date on macOS)
  date -d "$1 days" +%F 2>/dev/null || date -v"${1}d" +%F
}

add() {
  curl -fsS -X POST "$BASE_URL/api/items" -H 'Content-Type: application/json' -d "$1" >/dev/null
  echo "added: $(echo "$1" | sed -E 's/.*"name":"([^"]+)".*/\1/')"
}

add "{\"name\":\"Toned milk\",\"category\":\"Dairy\",\"location\":\"Fridge\",\"quantity\":1,\"unit\":\"L\",\"min_quantity\":1,\"expiry_date\":\"$(day 1)\"}"
add "{\"name\":\"Paneer\",\"category\":\"Dairy\",\"location\":\"Fridge\",\"quantity\":200,\"unit\":\"g\",\"expiry_date\":\"$(day 3)\"}"
add "{\"name\":\"Spinach\",\"category\":\"Produce\",\"location\":\"Fridge\",\"quantity\":1,\"unit\":\"pack\",\"expiry_date\":\"$(day -1)\",\"notes\":\"Use in dal today or compost\"}"
add "{\"name\":\"Sourdough loaf\",\"category\":\"Bakery\",\"location\":\"Pantry\",\"quantity\":1,\"unit\":\"pcs\",\"expiry_date\":\"$(day 0)\"}"
add "{\"name\":\"Frozen peas\",\"category\":\"Frozen\",\"location\":\"Freezer\",\"quantity\":500,\"unit\":\"g\",\"expiry_date\":\"$(day 120)\"}"
add "{\"name\":\"Basmati rice\",\"category\":\"Grains & Pasta\",\"location\":\"Pantry\",\"quantity\":0.5,\"unit\":\"kg\",\"min_quantity\":1,\"expiry_date\":\"$(day 200)\"}"
add "{\"name\":\"Chickpeas (canned)\",\"category\":\"Canned & Jarred\",\"location\":\"Pantry\",\"quantity\":3,\"unit\":\"pcs\",\"expiry_date\":\"$(day 400)\"}"
add "{\"name\":\"Mango pickle\",\"category\":\"Spices & Condiments\",\"location\":\"Pantry\",\"quantity\":1,\"unit\":\"pcs\"}"
add "{\"name\":\"Chicken thighs\",\"category\":\"Meat & Fish\",\"location\":\"Freezer\",\"quantity\":1,\"unit\":\"kg\",\"expiry_date\":\"$(day 45)\"}"
add "{\"name\":\"Greek yogurt\",\"category\":\"Dairy\",\"location\":\"Fridge\",\"quantity\":2,\"unit\":\"pcs\",\"expiry_date\":\"$(day -3)\"}"
echo "done: open $BASE_URL"
