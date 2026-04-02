#!/usr/bin/env python3
"""Promote Mylar-valid intake archives into the Mylar handoff directory.

This utility scans a source intake tree, re-audits each `.cbz`, and moves only
archives that already satisfy the strict `mylar_import_valid` baseline into the
dedicated Mylar staging directory.

It does not attempt metadata repair or tagging. Candidate and unresolved files
remain in place for later processing or review.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cbz_audit import audit_cbz


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_DEST = Path("/mnt/phoenix/media/incoming/mylar-import")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/promote_mylar_import/reports")


@dataclass
class PromoteRow:
    cbz_path: str
    destination_path: str
    mylar_import_valid: int
    moved: int
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"promote_mylar_import_{ts}.csv"


def should_skip_webp(path: Path) -> bool:
    return "webp" in str(path).casefold()


def unique_destination(dest_dir: Path, source_name: str) -> Path:
    candidate = dest_dir / source_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 1
    while True:
        alt = dest_dir / f"{stem}__dup{index}{suffix}"
        if not alt.exists():
            return alt
        index += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Source directory to scan for .cbz files")
    parser.add_argument("--dest", default=str(DEFAULT_DEST), help="Destination directory for Mylar-ready files")
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of files to inspect")
    parser.add_argument("--dry-run", action="store_true", help="Report eligible promotions without moving files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    dest = Path(args.dest).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    rows: list[PromoteRow] = []
    count = 0
    for cbz_path in sorted(root.rglob("*.cbz")):
        if args.limit and count >= args.limit:
            break
        count += 1

        if should_skip_webp(cbz_path):
            rows.append(
                PromoteRow(
                    cbz_path=str(cbz_path),
                    destination_path="",
                    mylar_import_valid=0,
                    moved=0,
                    note="skipped_webp",
                )
            )
            continue

        audit = audit_cbz(cbz_path)
        if not audit.mylar_import_valid:
            rows.append(
                PromoteRow(
                    cbz_path=str(cbz_path),
                    destination_path="",
                    mylar_import_valid=0,
                    moved=0,
                    note="not_mylar_valid",
                )
            )
            continue

        target = unique_destination(dest, cbz_path.name)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(cbz_path), str(target))
        rows.append(
            PromoteRow(
                cbz_path=str(cbz_path),
                destination_path=str(target),
                mylar_import_valid=1,
                moved=0 if args.dry_run else 1,
                note="dry_run" if args.dry_run else "moved",
            )
        )

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["cbz_path", "destination_path", "mylar_import_valid", "moved", "note"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    eligible = sum(1 for row in rows if row.mylar_import_valid)
    moved = sum(1 for row in rows if row.moved)
    print(f"scan_root={root}")
    print(f"dest={dest}")
    print(f"report={report_path}")
    print(f"processed={len(rows)} eligible={eligible} moved={moved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
