#!/usr/bin/env python3
"""Compare reading-list cache entries against existing CBZ archives."""

from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_CACHE_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")
DEFAULT_COMICS_ROOT = Path("/mnt/phoenix/media/comics")
DEFAULT_IMPORT_ROOT = Path("/mnt/phoenix/media/incoming/mylar-import")

CV_PATTERNS = [
    re.compile(r"comicvine\.gamespot\.com/.*/4000-(\d+)", re.I),
    re.compile(r"CVDB[:\s#-]*(\d+)", re.I),
    re.compile(r"COMICID[:\s#-]*(\d+)", re.I),
]


@dataclass
class Row:
    source_root: str
    cbz_path: str
    series: str
    number: str
    comicvine_series_id: str
    comicvine_issue_id: str
    status: str
    detail: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"cbl_cache_vs_library_{ts}.csv"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_CACHE_DB), help="SQLite cache path")
    ap.add_argument("--report", default="", help="Optional CSV report path")
    ap.add_argument("--root", action="append", help="CBZ root to compare; may be repeated")
    return ap.parse_args()


def extract_cv(text: str) -> str:
    if not text:
        return ""
    for pattern in CV_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(1)
    return ""


def read_root_meta(cbz: Path) -> tuple[str, str, str, str]:
    try:
        with zipfile.ZipFile(cbz, "r") as zf:
            target = next((n for n in zf.namelist() if n.lower() == "comicinfo.xml"), None)
            if not target:
                return "", "", "", ""
            root = ET.fromstring(zf.read(target))
    except Exception:
        return "", "", "", ""

    def text(tag: str) -> str:
        el = root.find(tag)
        return (el.text or "").strip() if el is not None and el.text else ""

    return text("Series"), text("Number"), extract_cv(text("Notes")), extract_cv(text("Web"))


def scan_root(root: Path) -> dict[tuple[str, str], Path]:
    found: dict[tuple[str, str], Path] = {}
    if not root.exists():
        return found
    for cbz in sorted(root.rglob("*.cbz")):
        series, number, notes_cv, web_cv = read_root_meta(cbz)
        issue_id = notes_cv or web_cv
        if issue_id:
            found[(series.casefold(), issue_id)] = cbz
    return found


def count_files(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for _ in root.rglob("*.cbz"))


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    comics_root = DEFAULT_COMICS_ROOT.resolve()
    import_root = DEFAULT_IMPORT_ROOT.resolve()
    if args.root:
        roots = [Path(r).resolve() for r in args.root]
        if len(roots) == 1:
            comics_root = roots[0]
        elif len(roots) >= 2:
            comics_root, import_root = roots[0], roots[1]
    else:
        roots = [comics_root, import_root]

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows: list[Row] = []
    stats = Counter()
    by_source = defaultdict(Counter)

    try:
        comics_present = scan_root(comics_root)
        import_present = scan_root(import_root)
        comics_total = count_files(comics_root)
        import_total = count_files(import_root)
        cache_rows = conn.execute(
            "SELECT series, number, comicvine_series_id, comicvine_issue_id FROM cbl_issue_lookup"
        ).fetchall()
        for row in cache_rows:
            key = (str(row["series"]).casefold(), str(row["comicvine_issue_id"]).strip())
            in_comics = key in comics_present
            in_import = key in import_present
            if in_import and in_comics:
                status = "both"
                detail = f"import={import_present[key]} | comics={comics_present[key]}"
            elif in_import:
                status = "mylar_import_only"
                detail = str(import_present[key])
            elif in_comics:
                status = "comics_only"
                detail = str(comics_present[key])
            else:
                status = "missing"
                detail = ""
            stats[status] += 1
            source = "reading_lists_vs_library"
            by_source[source][status] += 1
            rows.append(
                Row(
                    source_root=source,
                    cbz_path=detail if detail else "",
                    series=str(row["series"]),
                    number=str(row["number"]),
                    comicvine_series_id=str(row["comicvine_series_id"]),
                    comicvine_issue_id=str(row["comicvine_issue_id"]),
                    status=status,
                    detail=detail,
                )
            )
    finally:
        conn.close()

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "source_root",
                "cbz_path",
                "series",
                "number",
                "comicvine_series_id",
                "comicvine_issue_id",
                "status",
                "detail",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    print(f"db={db_path}")
    print(f"report={report_path}")
    print(f"comics_root={comics_root}")
    print(f"import_root={import_root}")
    print(f"physical_counts={{'comics': {comics_total}, 'mylar_import': {import_total}}}")
    print(f"status_counts={dict(stats)}")
    print(f"by_source={ {k: dict(v) for k, v in by_source.items()} }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
