#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
DEST="${2:-/mnt/phoenix/media/incoming/mylar-import}"
LIMIT="${3:-500}"
CYCLES="${4:-1}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"
CACHE_DB="/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3"

cd "$REPO_ROOT"

latest_csv() {
  local pattern="$1"
  ls -1t $pattern 2>/dev/null | head -n 1 || true
}

summarize_audit() {
  local csv
  csv="$(latest_csv "/mnt/phoenix/staging/cbz_audit/reports/cbz_audit_*.csv")"
  if [ -z "$csv" ]; then
    echo "audit_summary=missing"
    return 0
  fi
  python3 - "$csv" <<'PY'
import csv, sys
from collections import Counter
path = sys.argv[1]
with open(path, newline='', encoding='utf-8') as fh:
    rows = list(csv.DictReader(fh))
notes = Counter(r['note'] for r in rows)
print(f"audit_report={path}")
print(f"audit_rows={len(rows)}")
print(f"audit_mylar_valid={sum(1 for r in rows if r['mylar_import_valid']=='1')}")
print(f"audit_comicinfo_root={sum(1 for r in rows if r['has_comicinfo_root']=='1')}")
print(f"audit_series_present={sum(1 for r in rows if r['series_present']=='1')}")
print(f"audit_issue_present={sum(1 for r in rows if r['issue_number_present']=='1')}")
print(f"audit_cv_ref={sum(1 for r in rows if r['comicvine_reference_present']=='1')}")
print(f"audit_top_notes={notes.most_common(5)}")
PY
}

summarize_pass1() {
  local csv
  csv="$(latest_csv "/mnt/phoenix/staging/pass1_write_comicinfo/reports/pass1_write_comicinfo_*.csv")"
  if [ -z "$csv" ]; then
    echo "pass1_summary=missing"
    return 0
  fi
  python3 - "$csv" <<'PY'
import csv, sys
from collections import Counter
path = sys.argv[1]
with open(path, newline='', encoding='utf-8') as fh:
    rows = list(csv.DictReader(fh))
notes = Counter(r['note'] for r in rows)
status = Counter(r['resolver_status'] for r in rows)
print(f"pass1_report={path}")
print(f"pass1_rows={len(rows)}")
print(f"pass1_write_attempted={sum(1 for r in rows if r['write_attempted']=='1')}")
print(f"pass1_write_ok={sum(1 for r in rows if r['write_ok']=='1')}")
print(f"pass1_status={dict(status)}")
print(f"pass1_top_notes={notes.most_common(5)}")
PY
}

summarize_promote() {
  local csv
  csv="$(latest_csv "/mnt/phoenix/staging/promote_mylar_import/reports/promote_mylar_import_*.csv")"
  if [ -z "$csv" ]; then
    echo "promote_summary=missing"
    return 0
  fi
  python3 - "$csv" <<'PY'
import csv, sys
from collections import Counter
path = sys.argv[1]
with open(path, newline='', encoding='utf-8') as fh:
    rows = list(csv.DictReader(fh))
notes = Counter(r['note'] for r in rows)
print(f"promote_report={path}")
print(f"promote_rows={len(rows)}")
print(f"promote_moved={sum(1 for r in rows if r['moved']=='1')}")
print(f"promote_eligible={sum(1 for r in rows if r['mylar_import_valid']=='1')}")
print(f"promote_top_notes={notes.most_common(5)}")
PY
}

echo "== Pre-pass =="
python3 utilities/prepass_normalize.py --root "$ROOT" --cache-db "$CACHE_DB"
summarize_audit

cycle=1
while [ "$cycle" -le "$CYCLES" ]; do
  echo "== Pass 1 cycle $cycle =="
  python3 utilities/pass1_write_comicinfo.py --root "$ROOT" --limit "$LIMIT"
  summarize_pass1

  echo "== Promote cycle $cycle =="
  python3 utilities/promote_mylar_import.py --root "$ROOT" --dest "$DEST"
  summarize_promote

  cycle=$((cycle + 1))
done
