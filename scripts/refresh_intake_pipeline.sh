#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
WORKERS="${2:-$(nproc)}"
LIMIT="${3:-0}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"
CACHE_DB="/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3"

if [[ "$LIMIT" -le 0 ]]; then
  LIMIT="$(find "$ROOT" -type f -iname '*.cbz' | wc -l | tr -d ' ')"
fi

cd "$REPO_ROOT"

echo "== Refresh CBL cache =="
python3 utilities/build_cbl_cache.py --root /home/rmleonard/Projects/CBL-ReadingLists --db "$CACHE_DB"

echo "== Prepass normalize =="
python3 utilities/prepass_normalize.py --root "$ROOT" --cache-db "$CACHE_DB"

echo "== CBZ audit before cleanup =="
python3 utilities/cbz_audit.py --root "$ROOT" --limit "$LIMIT"

echo "== Cleanup dry-run =="
./scripts/file_cleanup_parallel.sh "$ROOT" dry-run "$WORKERS"

latest_report="$(ls -1t data/reports/file_cleanup_*.json | head -n 1)"
echo "== Cleanup apply from report =="
./scripts/file_cleanup_apply.sh "$latest_report" "$WORKERS"

echo "== CBZ audit after cleanup =="
python3 utilities/cbz_audit.py --root "$ROOT" --limit "$LIMIT"

echo "== Pass 1 then promote =="
./scripts/pass1_then_promote.sh "$ROOT" "$LIMIT"
