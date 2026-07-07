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
from collections import Counter, defaultdict
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
DEFAULT_EXTRACT_TIMEOUT = 120
DEFAULT_SAFETY_BYTES = 2 * 1024**3
DEFAULT_EXCLUDES = (
    "cache",
    "duplicates",
    "metadata-review",
    "mylar-import",
)


@dataclass
class ConversionResult:
    src_cbr: str
    dst_cbz: str
    status: str
    detail: str = ""


@dataclass
class TriageResult:
    src_cbr: str
    status: str
    detail: str = ""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return report_dir / f"cbr_to_cbz_{ts}.csv"


def normalize_excludes(values: list[str]) -> tuple[str, ...]:
    return tuple(v.strip().lower() for v in values if v.strip())


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_extract_with_tool(
    src: Path,
    dst_dir: Path,
    tool: str,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[bytes]:
    if tool == "unrar":
        return subprocess.run(
            ["unrar", "x", "-o+", "-idq", str(src), str(dst_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    if tool == "unar":
        return subprocess.run(
            ["unar", "-q", "-f", "-o", str(dst_dir), str(src)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    return subprocess.run(
        ["7z", "x", "-y", str(src), f"-o{dst_dir}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
        check=False,
    )


def archive_relpath(root: Path, src: Path) -> Path:
    try:
        return src.relative_to(root)
    except ValueError:
        return Path(src.name)


def is_excluded(path: Path, excludes: tuple[str, ...]) -> bool:
    text = str(path).lower()
    return any(fragment in text for fragment in excludes)


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


def triage_one(src: Path, excludes: tuple[str, ...]) -> TriageResult:
    if is_excluded(src, excludes):
        return TriageResult(str(src), "excluded", "excluded_path")
    if src.with_suffix(".cbz").exists():
        return TriageResult(str(src), "skip_exists", "matching_cbz_exists")
    return TriageResult(str(src), "candidate", "")


def free_bytes_available(path: Path) -> int:
    return shutil.disk_usage(path).free


def classify_extract_failure(detail: str) -> str:
    lowered = detail.lower()
    if "timed out after" in lowered:
        return "extract_failed_timeout"
    if "attempted to read more data than was available" in lowered:
        return "extract_failed_corrupt"
    if "unsupported method" in lowered:
        return "extract_failed_unsupported"
    return "extract_failed"


def timeout_result(tool: str, timeout_seconds: int) -> subprocess.CompletedProcess[bytes]:
    detail = f"{tool} timed out after {timeout_seconds}s"
    return subprocess.CompletedProcess(args=[tool], returncode=124, stdout=b"", stderr=detail.encode())


def extract_with_fallback(
    src: Path,
    extracted: Path,
    timeout_seconds: int,
) -> tuple[subprocess.CompletedProcess[bytes], str]:
    attempted: list[str] = []
    last_result: subprocess.CompletedProcess[bytes] | None = None

    if command_exists("unrar"):
        attempted.append("unrar")
        try:
            last_result = run_extract_with_tool(src, extracted, "unrar", timeout_seconds)
        except subprocess.TimeoutExpired:
            last_result = timeout_result("unrar", timeout_seconds)
        if last_result.returncode == 0:
            return last_result, "unrar"
        shutil.rmtree(extracted, ignore_errors=True)
        ensure_dir(extracted)

    if command_exists("unar"):
        attempted.append("unar")
        try:
            last_result = run_extract_with_tool(src, extracted, "unar", timeout_seconds)
        except subprocess.TimeoutExpired:
            last_result = timeout_result("unar", timeout_seconds)
        if last_result.returncode == 0:
            return last_result, "unar"
        shutil.rmtree(extracted, ignore_errors=True)
        ensure_dir(extracted)

    attempted.append("7z")
    try:
        last_result = run_extract_with_tool(src, extracted, "7z", timeout_seconds)
    except subprocess.TimeoutExpired:
        last_result = timeout_result("7z", timeout_seconds)
    if last_result.returncode == 0:
        return last_result, "7z"
    return last_result, "+".join(attempted)


def convert_one(
    src: Path,
    scan_root: Path,
    staging_root: Path,
    tmp_root: Path,
    timeout_seconds: int,
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

    free_bytes = free_bytes_available(src.parent)
    required_bytes = src.stat().st_size * 2
    if free_bytes < required_bytes + DEFAULT_SAFETY_BYTES:
        return ConversionResult(
            str(src),
            str(dst_cbz),
            "skip_no_space",
            f"free={free_bytes}; required={required_bytes}; safety={DEFAULT_SAFETY_BYTES}",
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="extract_", dir=tmp_root))
    try:
        extracted = temp_dir / "payload"
        ensure_dir(extracted)

        result, extractor = extract_with_fallback(src, extracted, timeout_seconds)
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
        "--extract-timeout",
        type=int,
        default=DEFAULT_EXTRACT_TIMEOUT,
        help="Maximum seconds to allow each extractor invocation before failing over",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be converted without changing files",
    )
    parser.add_argument(
        "--triage-only",
        action="store_true",
        help="Only classify files and print a failure summary without converting anything",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Path fragment to exclude from processing; may be repeated",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scan_root = Path(args.root).resolve()
    staging_root = Path(args.staging).resolve()
    tmp_root = Path(args.tmp_root).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    excludes = normalize_excludes(list(DEFAULT_EXCLUDES) + list(args.exclude))

    if not scan_root.exists():
        print(f"scan root does not exist: {scan_root}", file=sys.stderr)
        return 2

    rows: list[ConversionResult] = []
    triage_rows: list[TriageResult] = []
    processed = 0

    for src in iter_cbr_files(scan_root):
        if args.limit and processed >= args.limit:
            break
        if args.triage_only:
            triage_rows.append(triage_one(src, excludes))
            processed += 1
            continue
        if is_excluded(src, excludes):
            rows.append(ConversionResult(str(src), str(src.with_suffix(".cbz")), "excluded", "excluded_path"))
            processed += 1
            continue
        rows.append(
            convert_one(
                src,
                scan_root,
                staging_root,
                tmp_root,
                args.extract_timeout,
                args.dry_run,
            )
        )
        processed += 1

    write_report(report_path, rows)

    if args.triage_only:
        failure_counts = Counter(row.status for row in triage_rows)
        folder_counts = defaultdict(Counter)
        for row in triage_rows:
            folder_counts[Path(row.src_cbr).parent.name][row.status] += 1
        print(f"scan_root={scan_root}")
        print(f"report={report_path}")
        print(f"processed={len(triage_rows)} triage_only=1")
        for status, count in sorted(failure_counts.items()):
            print(f"{status}={count}")
        print("by_folder=")
        for folder, counts in sorted(folder_counts.items()):
            summary = ", ".join(f"{status}:{count}" for status, count in sorted(counts.items()))
            print(f"  {folder}: {summary}")
        return 0

    converted = sum(1 for row in rows if row.status == "converted")
    skipped = sum(1 for row in rows if row.status == "skip_exists")
    excluded = sum(1 for row in rows if row.status == "excluded")
    failed = sum(1 for row in rows if row.status not in {"converted", "skip_exists", "dry_run", "excluded"})
    dry_run = sum(1 for row in rows if row.status == "dry_run")

    print(f"scan_root={scan_root}")
    print(f"report={report_path}")
    print(f"processed={len(rows)} converted={converted} skipped={skipped} excluded={excluded} dry_run={dry_run} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
