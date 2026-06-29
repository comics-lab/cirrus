#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/rmleonard/Projects/cirrus"
cd "$REPO_ROOT"
python3 utilities/cbl_cache_presence_summary.py "$@"
