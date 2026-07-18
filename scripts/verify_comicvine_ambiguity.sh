#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/rmleonard/Projects/cirrus"
DB="${1:-$REPO_ROOT/data/cbl_lookup.sqlite3}"
MODE="${2:-report}"
REPORT="${3:-}"
LIMIT="${4:-0}"
DELAY="${5:-2.0}"

cd "$REPO_ROOT"

args=(python3 utilities/verify_comicvine_ambiguity.py --db "$DB" --delay-seconds "$DELAY")

if [[ -n "$REPORT" ]]; then
  args+=(--report "$REPORT")
fi

if [[ "$LIMIT" -gt 0 ]]; then
  args+=(--limit "$LIMIT")
fi

exec "${args[@]}"
