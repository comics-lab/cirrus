#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
DEST="${2:-/mnt/phoenix/media/incoming/mylar-import}"
LIMIT="${3:-500}"
CYCLES="${4:-1}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"
CACHE_DB="/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3"

cd "$REPO_ROOT"

echo "== Pre-pass =="
python3 utilities/prepass_normalize.py --root "$ROOT" --cache-db "$CACHE_DB"

cycle=1
while [ "$cycle" -le "$CYCLES" ]; do
  echo "== Pass 1 cycle $cycle =="
  python3 utilities/pass1_write_comicinfo.py --root "$ROOT" --limit "$LIMIT"

  echo "== Promote cycle $cycle =="
  python3 utilities/promote_mylar_import.py --root "$ROOT" --dest "$DEST"

  cycle=$((cycle + 1))
done
