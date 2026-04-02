#!/usr/bin/env python3
"""Convert CBR intake archives to CBZ for the current Cirrus workflow.

Default behavior:
- scan `/mnt/phoenix/media/incoming/jdownloader`
- recurse into package subdirectories
- convert `.cbr` files in place to `.cbz`
- stage successfully converted originals under `/mnt/phoenix/staging/cbr_to_cbz/originals`
- write a CSV report under `/mnt/phoenix/staging/cbr_to_cbz/reports`

This utility is intentionally conservative:
- existing `.cbz` targets are not overwritten
- originals are moved only after the new `.cbz` passes verification
- extraction work happens under a temp directory
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_STAGING = Path("/mnt/phoenix/staging/cbr_to_cbz/originals")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/cbr_to_cbz/reports")
DEFAULT_TMP_ROOT = Path("/tmp/cirrus-cbr-to-cbz")


@dataclass
class ConversionResult:
    src_cbr: str
    dst_cbz: str
    status: str
    detail: str = ""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return report_dir / f"cbr_to_cbz_{ts}.csv"


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_extract_with_tool(src: Path, dst_dir: Path, tool: str) -> subprocess.CompletedProcess[bytes]:
    if tool == "unar":
        return subprocess.run(
            ["unar", "-q", "-f", "-o", str(dst_dir), str(src)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=900,
            check=False,
        )
    return subprocess.run(
        ["7z", "x", "-y", str(src), f"-o{dst_dir}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        check=False,
    )


def archive_relpath(root: Path, src: Path) -> Path:
    try:
        return src.relative_to(root)
    except ValueError:
        return Path(src.name)


def zip_tree(source_dir: Path, dst_cbz: Path) -> None:
    with zipfile.ZipFile(dst_cbz, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(source_dir.rglob("*")):
            if item.is_dir():
                continue
            zf.write(item, item.relative_to(source_dir))


def verify_cbz(path: Path) -> tuple[bool, str]:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            bad_member = zf.testzip()
            if bad_member is not None:
                return False, f"bad_member:{bad_member}"
    except zipfile.BadZipFile:
        return False, "BadZipFile"
    except Exception as exc:  # pragma: no cover - defensive path
        return False, str(exc)
    return True, ""


def classify_extract_failure(detail: str) -> str:
    lowered = detail.lower()
    if "attempted to read more data than was available" in lowered:
        return "extract_failed_corrupt"
    if "unsupported method" in lowered:
        return "extract_failed_unsupported"
    return "extract_failed"


def extract_with_fallback(src: Path, extracted: Path) -> tuple[subprocess.CompletedProcess[bytes], str]:
    attempted: list[str] = []
    last_result: subprocess.CompletedProcess[bytes] | None = None

    if command_exists("unar"):
        attempted.append("unar")
        last_result = run_extract_with_tool(src, extracted, "unar")
        if last_result.returncode == 0:
            return last_result, "unar"
        shutil.rmtree(extracted, ignore_errors=True)
        ensure_dir(extracted)

    attempted.append("7z")
    last_result = run_extract_with_tool(src, extracted, "7z")
    if last_result.returncode == 0:
        return last_result, "7z"
    return last_result, "+".join(attempted)


def convert_one(
    src: Path,
    scan_root: Path,
    staging_root: Path,
    tmp_root: Path,
    dry_run: bool,
) -> ConversionResult:
    dst_cbz = src.with_suffix(".cbz")
    if dst_cbz.exists():
        return ConversionResult(str(src), str(dst_cbz), "skip_exists")

    rel = archive_relpath(scan_root, src)
    staged_original = staging_root / rel

    if dry_run:
        return ConversionResult(str(src), str(dst_cbz), "dry_run", str(staged_original))

    ensure_dir(staged_original.parent)
    ensure_dir(tmp_root)

    temp_dir = Path(tempfile.mkdtemp(prefix="extract_", dir=tmp_root))
    try:
        extracted = temp_dir / "payload"
        ensure_dir(extracted)

        result, extractor = extract_with_fallback(src, extracted)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).decode(errors="ignore").strip()[:500]
            if extractor:
                detail = f"extractor={extractor}; {detail}"[:500]
            status = classify_extract_failure(detail)
            return ConversionResult(str(src), str(dst_cbz), status, detail)

        zip_tree(extracted, dst_cbz)

        ok, detail = verify_cbz(dst_cbz)
        if not ok:
            dst_cbz.unlink(missing_ok=True)
            return ConversionResult(str(src), str(dst_cbz), "verify_failed", detail)

        shutil.move(str(src), str(staged_original))
        return ConversionResult(str(src), str(dst_cbz), "converted", f"extractor={extractor}; staged={staged_original}")
    except Exception as exc:  # pragma: no cover - defensive path
        dst_cbz.unlink(missing_ok=True)
        return ConversionResult(str(src), str(dst_cbz), "error", str(exc))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def iter_cbr_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".cbr":
            yield path


def write_report(report_path: Path, rows: list[ConversionResult]) -> None:
    ensure_dir(report_path.parent)
    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["src_cbr", "dst_cbz", "status", "detail"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "src_cbr": row.src_cbr,
                    "dst_cbz": row.dst_cbz,
                    "status": row.status,
                    "detail": row.detail,
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="Root directory to scan for .cbr files",
    )
    parser.add_argument(
        "--staging",
        default=str(DEFAULT_STAGING),
        help="Where successfully converted original .cbr files are moved",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional explicit CSV report path",
    )
    parser.add_argument(
        "--tmp-root",
        default=str(DEFAULT_TMP_ROOT),
        help="Temporary extraction root",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of .cbr files to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be converted without changing files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scan_root = Path(args.root).resolve()
    staging_root = Path(args.staging).resolve()
    tmp_root = Path(args.tmp_root).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    if not scan_root.exists():
        print(f"scan root does not exist: {scan_root}", file=sys.stderr)
        return 2

    rows: list[ConversionResult] = []
    processed = 0

    for src in iter_cbr_files(scan_root):
        if args.limit and processed >= args.limit:
            break
        rows.append(convert_one(src, scan_root, staging_root, tmp_root, args.dry_run))
        processed += 1

    write_report(report_path, rows)

    converted = sum(1 for row in rows if row.status == "converted")
    skipped = sum(1 for row in rows if row.status == "skip_exists")
    failed = sum(1 for row in rows if row.status not in {"converted", "skip_exists", "dry_run"})
    dry_run = sum(1 for row in rows if row.status == "dry_run")

    print(f"scan_root={scan_root}")
    print(f"report={report_path}")
    print(f"processed={len(rows)} converted={converted} skipped={skipped} dry_run={dry_run} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
