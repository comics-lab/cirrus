#!/usr/bin/env python3
"""Single-entry intake pipeline starting after CBR->CBZ conversion.

Stages:
- refresh ComicVine cache from CBL reading lists
- run prepass normalization
- run CBZ audit
- run cleanup dry-run
- replay cleanup apply from the saved report
- rerun CBZ audit
- run Pass 1 and promote

The only replay step is the cleanup report replay.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path("/home/rmleonard/Projects/cirrus")
CBL_ROOT = Path("/home/rmleonard/Projects/CBL-ReadingLists")
DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_CACHE_DB = REPO_ROOT / "data/cbl_lookup.sqlite3"
DEFAULT_REPORT_ROOT = REPO_ROOT / "data/reports"


@dataclass
class StageResult:
    name: str
    returncode: int
    stdout: str


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="Post-conversion CBZ root")
    ap.add_argument("--workers", type=int, default=0, help="Worker count for cleanup; default uses nproc")
    ap.add_argument("--limit", type=int, default=0, help="Limit for audit/pass1/promotion; default counts CBZ files")
    ap.add_argument("--dry-run", action="store_true", help="Run the pipeline without the final promote")
    return ap.parse_args()


def run_cmd(name: str, argv: list[str], cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> StageResult:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    print(f"== {name} ==")
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.returncode != 0:
        raise RuntimeError(f"{name} failed with exit code {proc.returncode}")
    return StageResult(name=name, returncode=proc.returncode, stdout=proc.stdout)


def count_cbz(root: Path) -> int:
    proc = subprocess.run(
        ["find", str(root), "-type", "f", "-iname", "*.cbz"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "failed to count cbz files")
    return sum(1 for line in proc.stdout.splitlines() if line.strip())


def latest_report(pattern: str) -> Path:
    matches = sorted(DEFAULT_REPORT_ROOT.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"no report matches {pattern}")
    return matches[-1]


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if args.workers > 0:
        workers = args.workers
    else:
        workers = int(subprocess.run(["nproc"], stdout=subprocess.PIPE, text=True, check=True).stdout.strip())
    limit = args.limit if args.limit > 0 else count_cbz(root)

    print(f"root={root}")
    print(f"workers={workers}")
    print(f"limit={limit}")

    run_cmd(
        "Refresh CBL cache",
        ["python3", "utilities/build_cbl_cache.py", "--root", str(CBL_ROOT), "--db", str(DEFAULT_CACHE_DB)],
    )
    run_cmd(
        "Prepass normalize",
        ["python3", "utilities/prepass_normalize.py", "--root", str(root), "--cache-db", str(DEFAULT_CACHE_DB)],
    )
    run_cmd(
        "CBZ audit before cleanup",
        ["python3", "utilities/cbz_audit.py", "--root", str(root), "--limit", str(limit)],
    )
    run_cmd(
        "Cleanup dry-run",
        ["./scripts/file_cleanup_parallel.sh", str(root), "dry-run", str(workers)],
    )
    cleanup_report = latest_report("file_cleanup_*.json")
    print(f"cleanup_report={cleanup_report}")
    run_cmd(
        "Cleanup apply",
        ["./scripts/file_cleanup_apply.sh", str(cleanup_report), str(workers)],
    )
    run_cmd(
        "CBZ audit after cleanup",
        ["python3", "utilities/cbz_audit.py", "--root", str(root), "--limit", str(limit)],
    )
    if args.dry_run:
        print("dry_run=1")
        return 0
    run_cmd(
        "Pass 1 then promote",
        ["./scripts/pass1_then_promote.sh", str(root), str(limit)],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
