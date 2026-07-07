#!/usr/bin/env bash
set -euo pipefail

REPORT="${1:?usage: file_cleanup_apply.sh /path/to/file_cleanup.json [workers]}"
WORKERS="${2:-8}"
ROOT="$(python3 - <<'PY' "$REPORT"
from pathlib import Path
import json, sys
report = Path(sys.argv[1]).resolve()
data = json.loads(report.read_text(encoding="utf-8"))
print(data["root"])
PY
)"

REPORT_PATH="$REPORT" exec "$(dirname "$0")/file_cleanup.sh" "$ROOT" apply "$WORKERS"
