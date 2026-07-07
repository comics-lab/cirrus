#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
LIMIT="${2:-0}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"

if [[ "$LIMIT" -le 0 ]]; then
  LIMIT="$(find "$ROOT" -type f -iname '*.cbz' | wc -l | tr -d ' ')"
fi

cd "$REPO_ROOT"
python3 utilities/pass1_write_comicinfo.py --root "$ROOT" --limit "$LIMIT"
