#!/usr/bin/env python3
"""Extract comic payloads from intake zip files and archive the zips.

Default behavior:
- scan `/mnt/phoenix/media/incoming/jdownloader` for `.zip`
- extract contained `.cbz`, `.cbr`, and `.pdf` files into the zip's parent dir
- ignore entries with `webp` in their names
- move the processed zip into `/mnt/phoenix/media/incoming/archive`

This utility is intentionally conservative:
- existing extracted payloads are not overwritten
- if no eligible payloads are found, the zip is left in place
- if any extraction step fails, the zip is left in place
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_ARCHIVE = Path("/mnt/phoenix/media/incoming/archive")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/extract_zip_payloads/reports")
VALID_SUFFIXES = {".cbz", ".cbr", ".pdf"}
DEFAULT_SAFETY_BYTES = 2 * 1024**3


@dataclass
class ExtractRow:
    zip_path: str
    archive_path: str
    payload_count: int
    extracted_count: int
    skipped_existing_count: int
    skipped_webp_count: int
    required_bytes: int
    free_bytes: int
    status: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"extract_zip_payloads_{ts}.csv"


def should_skip_entry(name: str) -> bool:
    return "webp" in name.casefold()


def should_skip_archive(zip_path: Path) -> bool:
    name = zip_path.name.casefold()
    if "webp" in name:
        return True
    return bool(re.search(r"\b20\d{2}\.\d{2}\.\d{2}\b.*\bweek\b|\bweek\b.*\b20\d{2}\.\d{2}\.\d{2}\b", name))


def target_for_member(parent: Path, member_name: str) -> Path:
    member_path = Path(member_name)
    if member_path.parent == Path("."):
        return parent / member_path.name
    return parent / member_path


def archive_destination(archive_root: Path, scan_root: Path, src: Path) -> Path:
    try:
        rel = src.relative_to(scan_root)
    except ValueError:
        rel = Path(src.name)
    return archive_root / rel


def free_bytes_for(path: Path) -> int:
    stat = path.stat()
    return stat.st_blocks * 512 if hasattr(stat, "st_blocks") else 0


def free_bytes_available(path: Path) -> int:
    usage = shutil.disk_usage(path)
    return usage.free


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan for .zip files")
    parser.add_argument("--archive", default=str(DEFAULT_ARCHIVE), help="Where processed zip files are moved")
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of zip files to process")
    parser.add_argument("--dry-run", action="store_true", help="Report work without extracting or moving files")
    return parser.parse_args()


def extract_one(zip_path: Path, scan_root: Path, archive_root: Path, dry_run: bool) -> ExtractRow:
    extracted_count = 0
    skipped_existing = 0
    skipped_webp = 0
    payload_count = 0
    required_bytes = 0
    free_bytes = 0
    archive_path = archive_destination(archive_root, scan_root, zip_path)
    parent = zip_path.parent

    if should_skip_archive(zip_path):
        return ExtractRow(
            zip_path=str(zip_path),
            archive_path=str(archive_path),
            payload_count=0,
            extracted_count=0,
            skipped_existing_count=0,
            skipped_webp_count=0,
            required_bytes=0,
            free_bytes=0,
            status="skip_webp_archive",
            note="webp_named_archive_left_in_place",
        )

    try:
        with zipfile.ZipFile(zip_path) as zf:
            members = [m for m in zf.infolist() if not m.is_dir()]
            payloads = []
            for member in members:
                if should_skip_entry(member.filename):
                    skipped_webp += 1
                    continue
                if Path(member.filename).suffix.casefold() in VALID_SUFFIXES:
                    payloads.append(member)
            payload_count = len(payloads)
            if not payloads:
                return ExtractRow(
                    zip_path=str(zip_path),
                    archive_path=str(archive_path),
                    payload_count=0,
                    extracted_count=0,
                    skipped_existing_count=0,
                    skipped_webp_count=skipped_webp,
                    required_bytes=0,
                    free_bytes=0,
                    status="no_payloads",
                    note="no_cbz_cbr_pdf_entries",
                )

            required_bytes = sum(member.file_size for member in payloads if not (target_for_member(parent, member.filename).exists()))
            free_bytes = free_bytes_available(parent)
            if not dry_run and free_bytes < required_bytes + DEFAULT_SAFETY_BYTES:
                return ExtractRow(
                    zip_path=str(zip_path),
                    archive_path=str(archive_path),
                    payload_count=payload_count,
                    extracted_count=0,
                    skipped_existing_count=skipped_existing,
                    skipped_webp_count=skipped_webp,
                    required_bytes=required_bytes,
                    free_bytes=free_bytes,
                    status="skip_no_space",
                    note="insufficient_free_space",
                )

            for member in payloads:
                target = target_for_member(parent, member.filename)
                if target.exists():
                    skipped_existing += 1
                    continue
                if dry_run:
                    extracted_count += 1
                    continue
                with zf.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted_count += 1

        if not dry_run:
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(zip_path), str(archive_path))

        return ExtractRow(
            zip_path=str(zip_path),
            archive_path=str(archive_path),
            payload_count=payload_count,
            extracted_count=extracted_count,
            skipped_existing_count=skipped_existing,
            skipped_webp_count=skipped_webp,
            required_bytes=required_bytes,
            free_bytes=free_bytes,
            status="dry_run" if dry_run else "archived",
            note="",
        )
    except zipfile.BadZipFile:
        return ExtractRow(
            zip_path=str(zip_path),
            archive_path=str(archive_path),
            payload_count=payload_count,
            extracted_count=extracted_count,
            skipped_existing_count=skipped_existing,
            skipped_webp_count=skipped_webp,
            required_bytes=required_bytes,
            free_bytes=free_bytes,
            status="bad_zip",
            note="BadZipFile",
        )
    except Exception as exc:
        return ExtractRow(
            zip_path=str(zip_path),
            archive_path=str(archive_path),
            payload_count=payload_count,
            extracted_count=extracted_count,
            skipped_existing_count=skipped_existing,
            skipped_webp_count=skipped_webp,
            required_bytes=required_bytes,
            free_bytes=free_bytes,
            status="error",
            note=str(exc),
        )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    archive_root = Path(args.archive).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    rows: list[ExtractRow] = []
    processed = 0
    for zip_path in sorted(root.rglob("*.zip")):
        if args.limit and processed >= args.limit:
            break
        rows.append(extract_one(zip_path, root, archive_root, args.dry_run))
        processed += 1

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "zip_path",
                "archive_path",
                "payload_count",
                "extracted_count",
                "skipped_existing_count",
                "skipped_webp_count",
                "required_bytes",
                "free_bytes",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    archived = sum(1 for row in rows if row.status == "archived")
    dry_run = sum(1 for row in rows if row.status == "dry_run")
    no_payloads = sum(1 for row in rows if row.status == "no_payloads")
    skip_no_space = sum(1 for row in rows if row.status == "skip_no_space")
    failed = sum(1 for row in rows if row.status in {"bad_zip", "error"})
    print(f"scan_root={root}")
    print(f"archive_root={archive_root}")
    print(f"report={report_path}")
    print(
        f"processed={len(rows)} archived={archived} dry_run={dry_run} "
        f"no_payloads={no_payloads} skip_no_space={skip_no_space} failed={failed}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
