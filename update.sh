#!/usr/bin/env bash
# Daily refresh: re-fetch Epoch data, rebuild docs/data.json, push if changed.
set -euo pipefail
cd "$(dirname "$0")"
python3 fetch_data.py
if ! git diff --quiet docs/data.json 2>/dev/null; then
  git add docs/data.json data/epoch_notable_ai_models.csv
  git commit -m "Update China compute data ($(date -u +%F))"
  git push
  echo "pushed update"
else
  echo "no data changes"
fi
