#!/usr/bin/env python3
"""Print a concise presence summary for the reading-list cache."""

from __future__ import annotations

import argparse
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_CACHE_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_COMICS_ROOT = Path("/mnt/phoenix/media/comics")
DEFAULT_IMPORT_ROOT = Path("/mnt/phoenix/media/incoming/mylar-import")
CV_PATTERNS = [
    r"comicvine\.gamespot\.com/.*/4000-(\d+)",
    r"CVDB[:\s#-]*(\d+)",
    r"COMICID[:\s#-]*(\d+)",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_CACHE_DB))
    ap.add_argument("--comics-root", default=str(DEFAULT_COMICS_ROOT))
    ap.add_argument("--import-root", default=str(DEFAULT_IMPORT_ROOT))
    return ap.parse_args()


def extract_cv(text: str) -> str:
    if not text:
        return ""
    lowered = text.lower()
    upper = text.upper()
    for pattern in CV_PATTERNS:
        import re

        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1)
    if "comicvine" in lowered or "cvdb" in upper or "comicid" in upper:
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits
    return ""


def build_present_set(root: Path) -> set[tuple[str, str]]:
    present: set[tuple[str, str]] = set()
    if not root.exists():
        return present
    for cbz in root.rglob("*.cbz"):
        try:
            with zipfile.ZipFile(cbz, "r") as zf:
                target = next((n for n in zf.namelist() if n.lower() == "comicinfo.xml"), None)
                if not target:
                    continue
                root_xml = ET.fromstring(zf.read(target))
                series = ((root_xml.findtext("Series") or "").strip()).casefold()
                notes = (root_xml.findtext("Notes") or "").strip()
                web = (root_xml.findtext("Web") or "").strip()
                issue = extract_cv(notes) or extract_cv(web)
                if issue:
                    present.add((series, issue))
        except Exception:
            continue
    return present


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()
    comics_root = Path(args.comics_root).resolve()
    import_root = Path(args.import_root).resolve()

    comics_total = sum(1 for _ in comics_root.rglob("*.cbz")) if comics_root.exists() else 0
    import_total = sum(1 for _ in import_root.rglob("*.cbz")) if import_root.exists() else 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cache_rows = conn.execute(
            "SELECT series, comicvine_issue_id FROM cbl_issue_lookup"
        ).fetchall()
        comics_present = build_present_set(comics_root)
        import_present = build_present_set(import_root)
        comics_only = 0
        import_only = 0
        both = 0
        for row in cache_rows:
            key = (str(row["series"]).casefold(), str(row["comicvine_issue_id"]).strip())
            in_comics = key in comics_present
            in_import = key in import_present
            if in_comics and in_import:
                both += 1
            elif in_import:
                import_only += 1
            elif in_comics:
                comics_only += 1
    finally:
        conn.close()

    print(f"physical_counts={{'comics': {comics_total}, 'mylar_import': {import_total}}}")
    print(f"cache_present_counts={{'mylar_import_only': {import_only}, 'comics_only': {comics_only}, 'both': {both}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
