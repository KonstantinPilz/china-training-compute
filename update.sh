#!/usr/bin/env bash
# Daily refresh: re-fetch Epoch data, rebuild docs/data.json, push if changed.
set -euo pipefail
cd "$(dirname "$0")"
python3 fetch_data.py
# Glob the mirror rather than naming files: a new Epoch CSV must never be left
# uncommitted, which is how the mirror silently went partial before (see data/README.md).
if ! git diff --quiet docs/data.json data/epoch_*.csv 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard data/)" ]; then
  git add docs/data.json data/epoch_*.csv
  git commit -m "Update China compute data ($(date -u +%F))"
  git push
  echo "pushed update"
else
  echo "no data changes"
fi
