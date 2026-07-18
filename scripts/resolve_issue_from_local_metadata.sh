#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/rmleonard/Projects/cirrus"
ROOT="${1:-}"
REPORT="${2:-}"
LIMIT="${3:-0}"
GCD_DB="${4:-/home/rmleonard/Projects/mylar-library/utilities/2025-10-15.db}"

cd "$REPO_ROOT"

args=(python3 utilities/resolve_issue_from_local_metadata.py --gcd-db "$GCD_DB")

if [[ -n "$ROOT" ]]; then
  args+=(--root "$ROOT")
fi

if [[ -n "$REPORT" ]]; then
  args+=(--report "$REPORT")
fi

if [[ "$LIMIT" -gt 0 ]]; then
  args+=(--limit "$LIMIT")
fi

exec "${args[@]}"
