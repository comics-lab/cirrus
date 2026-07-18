#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
IMPORT_ROOT="${2:-/mnt/phoenix/media/incoming/mylar-imports}"
MODE="${3:-dry-run}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"
REPORT="${4:-}"

cd "$REPO_ROOT"

args=(python3 utilities/mylar_v3_buildout.py --source-root "$ROOT" --import-root "$IMPORT_ROOT")

if [[ -n "$REPORT" ]]; then
  args+=(--report "$REPORT")
fi

case "$MODE" in
  dry-run|--dry-run)
    args+=(--dry-run)
    ;;
  promote)
    args+=(--promote)
    ;;
  move)
    args+=(--promote --move)
    ;;
  *)
    echo "usage: $0 [source-root] [import-root] [dry-run|promote|move] [report]" >&2
    exit 2
    ;;
esac

exec "${args[@]}"
