#!/usr/bin/env python3
"""Rebuild normalized CBZ files from extracted image folders in quarantine.

Default behavior:
- scan `/mnt/phoenix/media/incoming/cbr-quarantine`
- ignore the `duplicates/` subtree
- find extracted image folders that sit beside quarantine `.cbr` files
- rebuild `.cbz` files with images at archive root
- verify each rebuilt archive
- delete the extracted working folder only after a clean rebuild

This utility keeps the original `.cbr` files in place.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/cbr-quarantine")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/rebuild_quarantine_cbz/reports")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
PAGE_SUFFIX_RE = re.compile(r"^(?P<base>.+?)(?:[-_ ]\d{3,5})$")


@dataclass
class RebuildRow:
    image_dir: str
    dst_cbz: str
    image_count: int
    status: str
    note: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ensure_dir(report_dir)
    return report_dir / f"rebuild_quarantine_cbz_{ts}.csv"


def image_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def infer_output_name(image_dir: Path, parent: Path) -> Path:
    sibling_cbr = parent / f"{image_dir.name}.cbr"
    if sibling_cbr.exists():
        return sibling_cbr.with_suffix(".cbz")

    files = image_files(image_dir)
    if not files:
        return parent / f"{image_dir.name}.cbz"

    stem = files[0].stem
    match = PAGE_SUFFIX_RE.match(stem)
    if match:
        return parent / f"{match.group('base')}.cbz"
    return parent / f"{image_dir.name}.cbz"


def verify_cbz(path: Path) -> tuple[bool, str]:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            bad_member = zf.testzip()
            if bad_member is not None:
                return False, f"bad_member:{bad_member}"
    except zipfile.BadZipFile:
        return False, "BadZipFile"
    except Exception as exc:  # pragma: no cover - defensive
        return False, str(exc)
    return True, ""


def build_cbz(image_dir: Path, dst_cbz: Path) -> tuple[bool, str]:
    files = image_files(image_dir)
    if not files:
        return False, "no_images"

    with tempfile.TemporaryDirectory(dir="/tmp", prefix="rebuild_quarantine_") as tmp:
        tmp_path = Path(tmp)
        rebuilt = tmp_path / "rebuilt.cbz"
        with zipfile.ZipFile(rebuilt, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in files:
                zf.write(item, item.name)

        ok, detail = verify_cbz(rebuilt)
        if not ok:
            return False, detail
        shutil.move(str(rebuilt), str(dst_cbz))
    return True, ""


def candidate_dirs(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for child in sorted(root.rglob("*")):
        if not child.is_dir():
            continue
        if "duplicates" in child.parts:
            continue
        if child == root:
            continue
        if image_files(child):
            candidates.append(child)
    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Quarantine root to scan")
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of folders to rebuild")
    parser.add_argument("--dry-run", action="store_true", help="Report work without writing archives or deleting folders")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    report = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    if not root.exists():
        print(f"quarantine root does not exist: {root}", file=sys.stderr)
        return 2

    rows: list[RebuildRow] = []
    processed = 0

    for image_dir in candidate_dirs(root):
        if args.limit and processed >= args.limit:
            break
        parent = image_dir.parent
        dst_cbz = infer_output_name(image_dir, parent)
        files = image_files(image_dir)
        image_count = len(files)

        if dst_cbz.exists():
            rows.append(
                RebuildRow(str(image_dir), str(dst_cbz), image_count, "skip_exists", "")
            )
            processed += 1
            continue

        if args.dry_run:
            rows.append(
                RebuildRow(str(image_dir), str(dst_cbz), image_count, "dry_run", "")
            )
            processed += 1
            continue

        ok, detail = build_cbz(image_dir, dst_cbz)
        if not ok:
            dst_cbz.unlink(missing_ok=True)
            rows.append(
                RebuildRow(str(image_dir), str(dst_cbz), image_count, "build_failed", detail)
            )
            processed += 1
            continue

        shutil.rmtree(image_dir)
        rows.append(
            RebuildRow(str(image_dir), str(dst_cbz), image_count, "rebuilt", "")
        )
        processed += 1

    ensure_dir(report.parent)
    with report.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["image_dir", "dst_cbz", "image_count", "status", "note"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    rebuilt = sum(1 for row in rows if row.status == "rebuilt")
    skipped = sum(1 for row in rows if row.status == "skip_exists")
    failed = sum(1 for row in rows if row.status == "build_failed")
    dry_run = sum(1 for row in rows if row.status == "dry_run")

    print(f"quarantine_root={root}")
    print(f"report={report}")
    print(f"processed={len(rows)} rebuilt={rebuilt} skipped={skipped} dry_run={dry_run} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
