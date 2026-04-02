#!/usr/bin/env python3
"""Audit CBZ intake archives for metadata placement and basic validity.

Current default focus:
- scan `/mnt/phoenix/media/incoming/jdownloader`
- inspect `.cbz` files only
- detect root vs nested `ComicInfo.xml` / `MetronInfo.xml`
- parse root `ComicInfo.xml` when present
- report whether a likely ComicVine reference is present

This is intentionally a first-pass audit utility, not the final metadata
enrichment pipeline.
"""

from __future__ import annotations

import argparse
import csv
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/cbz_audit/reports")

CV_PATTERNS = [
    re.compile(r"comicvine\.gamespot\.com/.*/4000-(\d+)", re.I),
    re.compile(r"CVDB[:\s#-]*(\d+)", re.I),
    re.compile(r"COMICID[:\s#-]*(\d+)", re.I),
]


@dataclass
class AuditRow:
    cbz_path: str
    has_comicinfo_root: int
    has_metroninfo_root: int
    comicinfo_in_subfolders: int
    metroninfo_in_subfolders: int
    has_subfolders: int
    comicinfo_parse_ok: int
    comicvine_reference_present: int
    comicvine_reference_value: str
    series: str
    issue_number: str
    year: str
    publisher: str
    note: str


def split_path(value: str) -> list[str]:
    return [part for part in value.replace("\\", "/").split("/") if part]


def extract_comicvine_reference(fields: list[str]) -> str:
    for field in fields:
        if not field:
            continue
        for pattern in CV_PATTERNS:
            match = pattern.search(field)
            if match:
                return match.group(1)
    return ""


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"cbz_audit_{ts}.csv"


def audit_cbz(path: Path) -> AuditRow:
    has_subfolders = False
    ci_root = False
    mi_root = False
    ci_nested = False
    mi_nested = False
    comicinfo_parse_ok = 0
    comicvine_reference_present = 0
    comicvine_reference_value = ""
    series = ""
    issue_number = ""
    year = ""
    publisher = ""
    note = ""

    try:
        with zipfile.ZipFile(path, "r") as zf:
            root_comicinfo_name = None
            for name in zf.namelist():
                parts = split_path(name)
                if len(parts) > 1:
                    has_subfolders = True
                if not parts:
                    continue
                fname = parts[-1].lower()
                is_root = len(parts) == 1
                if fname == "comicinfo.xml":
                    if is_root:
                        ci_root = True
                        root_comicinfo_name = name
                    else:
                        ci_nested = True
                elif fname == "metroninfo.xml":
                    if is_root:
                        mi_root = True
                    else:
                        mi_nested = True

            if root_comicinfo_name:
                data = zf.read(root_comicinfo_name)
                root = ET.fromstring(data)
                comicinfo_parse_ok = 1

                def text(tag: str) -> str:
                    node = root.find(tag)
                    return (node.text or "").strip() if node is not None and node.text else ""

                series = text("Series")
                issue_number = text("Number")
                year = text("Year")
                publisher = text("Publisher")
                reference = extract_comicvine_reference([text("Web"), text("Notes")])
                if reference:
                    comicvine_reference_present = 1
                    comicvine_reference_value = reference

    except zipfile.BadZipFile:
        note = "BadZipFile"
    except ET.ParseError as exc:
        note = f"ComicInfo ParseError: {exc}"
    except Exception as exc:  # pragma: no cover - defensive path
        note = str(exc)

    return AuditRow(
        cbz_path=str(path),
        has_comicinfo_root=int(ci_root),
        has_metroninfo_root=int(mi_root),
        comicinfo_in_subfolders=int(ci_nested),
        metroninfo_in_subfolders=int(mi_nested),
        has_subfolders=int(has_subfolders),
        comicinfo_parse_ok=comicinfo_parse_ok,
        comicvine_reference_present=comicvine_reference_present,
        comicvine_reference_value=comicvine_reference_value,
        series=series,
        issue_number=issue_number,
        year=year,
        publisher=publisher,
        note=note,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="Root directory to scan for .cbz files",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional explicit CSV report path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of .cbz files to inspect",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    rows: list[AuditRow] = []

    count = 0
    for path in sorted(root.rglob("*.cbz")):
        if args.limit and count >= args.limit:
            break
        rows.append(audit_cbz(path))
        count += 1

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cbz_path",
                "has_comicinfo_root",
                "has_metroninfo_root",
                "comicinfo_in_subfolders",
                "metroninfo_in_subfolders",
                "has_subfolders",
                "comicinfo_parse_ok",
                "comicvine_reference_present",
                "comicvine_reference_value",
                "series",
                "issue_number",
                "year",
                "publisher",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    with_comicinfo = sum(1 for row in rows if row.has_comicinfo_root)
    valid_parse = sum(1 for row in rows if row.comicinfo_parse_ok)
    with_cv = sum(1 for row in rows if row.comicvine_reference_present)
    print(f"scan_root={root}")
    print(f"report={report_path}")
    print(f"processed={len(rows)} comicinfo_root={with_comicinfo} parse_ok={valid_parse} comicvine_ref={with_cv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
