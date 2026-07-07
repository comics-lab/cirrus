#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
MODE="${2:-dry-run}"
WORKERS="${3:-$(nproc)}"

exec "$(dirname "$0")/file_cleanup.sh" "$ROOT" "$MODE" "$WORKERS"
