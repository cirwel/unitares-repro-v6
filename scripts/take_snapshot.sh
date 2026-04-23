#!/usr/bin/env bash
# Take a fresh verdict-counterfactual snapshot, append to the dataset.
#
# This is intentionally a manual helper, not a cron. Run it when you want
# another data point on the drift question for v7. Monthly cadence is a
# reasonable default; weekly if something interesting seems to be happening.
#
# Usage:  ./scripts/take_snapshot.sh
# Effect: writes data/verdict_counterfactual_<YYYY-MM-DD>.csv, commits to
#         git, and (if `hf` is authenticated) pushes to the HF dataset.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

TODAY="$(date +%Y-%m-%d)"
OUT="data/verdict_counterfactual_${TODAY}.csv"

if [[ -f "$OUT" ]]; then
  echo "Snapshot for $TODAY already exists at $OUT. Nothing to do." >&2
  exit 0
fi

echo "[snapshot] Running counterfactual for window ending now..." >&2
python3 scripts/verdict_counterfactual.py --window-days 30 \
  --csv --output "$OUT"

# Capture summary for commit message
SUMMARY="$(python3 scripts/verdict_counterfactual.py --window-days 30 2>&1 \
  | grep -E '^Total (rows|flips)' | tr '\n' ' ')"

echo "[snapshot] $OUT written. $SUMMARY" >&2

# Local git commit
git add "$OUT"
git commit -m "data: snapshot ${TODAY}

${SUMMARY}"

# Push to GitHub
if git remote get-url origin >/dev/null 2>&1; then
  git push origin main
fi

# Push to HF dataset (if authenticated)
if command -v hf >/dev/null 2>&1 && hf auth whoami >/dev/null 2>&1; then
  hf upload hikewa/unitares-verdict-counterfactual-v6.8 "$OUT" "$OUT" \
    --type dataset \
    --commit-message "data: snapshot ${TODAY}" \
    --quiet || echo "[snapshot] HF upload failed — GH push succeeded." >&2
fi

echo "[snapshot] done." >&2
