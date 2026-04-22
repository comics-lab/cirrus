#!/usr/bin/env python3
"""Slow, one-file-at-a-time Mylar importer for large pre-tagged batches.

This is intended for bulk trees that are already mostly Mylar-valid, where the
goal is to avoid dropping a large basket into Mylar at once and to keep
ComicVine/API activity paced.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_MYlar_URL = "http://192.168.1.113:8090"
DEFAULT_CONFIG = "/mnt/phoenix/services/mylar/mylar/config.ini"
DEFAULT_QUEUE_HOST = "/mnt/phoenix/media/incoming/mylar-import/paced-batch"
DEFAULT_QUEUE_MYLAR = "/mylar-imports/paced-batch"
DEFAULT_REJECT_HOST = "/mnt/phoenix/media/incoming/mylar-import/paced-rejects"
DEFAULT_LOG = "/tmp/mylar_paced_import.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage one file at a time into Mylar and pace forceProcess calls."
    )
    parser.add_argument("--source-root", required=True, help="Host path to source tree")
    parser.add_argument(
        "--exclude-csv",
        help="CSV file with a path column naming holdback files to exclude",
    )
    parser.add_argument(
        "--mylar-url",
        default=DEFAULT_MYlar_URL,
        help=f"Mylar base URL (default: {DEFAULT_MYlar_URL})",
    )
    parser.add_argument(
        "--mylar-config",
        default=DEFAULT_CONFIG,
        help=f"Mylar config.ini path used to read API key (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument("--api-key", help="Override Mylar API key instead of reading config")
    parser.add_argument(
        "--queue-dir-host",
        default=DEFAULT_QUEUE_HOST,
        help=f"Host staging directory visible to Mylar (default: {DEFAULT_QUEUE_HOST})",
    )
    parser.add_argument(
        "--queue-dir-mylar",
        default=DEFAULT_QUEUE_MYLAR,
        help=f"Container-visible path passed to forceProcess (default: {DEFAULT_QUEUE_MYLAR})",
    )
    parser.add_argument(
        "--reject-dir-host",
        default=DEFAULT_REJECT_HOST,
        help=f"Host path for files Mylar leaves behind or times out on (default: {DEFAULT_REJECT_HOST})",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "move"),
        default="copy",
        help="Whether to copy or move files into the queue dir (default: copy)",
    )
    parser.add_argument(
        "--cooldown-seconds",
        type=int,
        default=60,
        help="Sleep between items after forceProcess completes or times out (default: 60)",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=5,
        help="How often to poll the queue dir for file removal (default: 5)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=600,
        help="How long to wait for Mylar to consume a staged file before rejecting it (default: 600)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional max number of files to process this run",
    )
    parser.add_argument(
        "--log",
        default=DEFAULT_LOG,
        help=f"CSV log path (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned work without staging files or calling Mylar",
    )
    return parser.parse_args()


def read_api_key(config_path: str) -> str:
    cfg = configparser.ConfigParser()
    if not cfg.read(config_path):
        raise RuntimeError(f"Unable to read Mylar config: {config_path}")
    key = cfg.get("API", "api_key", fallback="").strip()
    if not key:
        raise RuntimeError(f"No API key found in {config_path}")
    return key


def load_exclusions(path: str | None) -> set[str]:
    if not path:
        return set()
    exclusions: set[str] = set()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidate = row.get("path") or row.get("cbz_path") or row.get("rel_path")
            if candidate:
                exclusions.add(os.path.normpath(candidate))
    return exclusions


def build_candidates(source_root: Path, exclusions: set[str]) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(source_root.rglob("*.cbz")):
        if os.path.normpath(str(path)) in exclusions:
            continue
        candidates.append(path)
    return candidates


def ensure_empty_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    leftovers = [p for p in path.iterdir()]
    if leftovers:
        raise RuntimeError(f"Queue directory is not empty: {path}")


def append_log(log_path: Path, row: dict[str, str]) -> None:
    exists = log_path.exists()
    with log_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "source_path",
                "staged_path",
                "mode",
                "status",
                "detail",
            ],
        )
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def force_process(mylar_url: str, api_key: str, queue_dir_mylar: str) -> str:
    params = {
        "apikey": api_key,
        "cmd": "forceProcess",
        "nzb_name": "Manual Run",
        "nzb_folder": queue_dir_mylar,
    }
    url = f"{mylar_url.rstrip('/')}/api?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def stage_file(src: Path, dst_dir: Path, mode: str) -> Path:
    dst = dst_dir / src.name
    if dst.exists():
        raise RuntimeError(f"Destination already exists: {dst}")
    if mode == "copy":
        shutil.copy2(src, dst)
    else:
        shutil.move(src, dst)
    return dst


def wait_for_consumption(staged: Path, timeout_seconds: int, poll_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not staged.exists():
            return True
        time.sleep(poll_seconds)
    return not staged.exists()


def reject_file(staged: Path, reject_root: Path) -> Path:
    reject_root.mkdir(parents=True, exist_ok=True)
    dst = reject_root / staged.name
    if dst.exists():
        stem = staged.stem
        suffix = staged.suffix
        i = 1
        while True:
            candidate = reject_root / f"{stem}.{i}{suffix}"
            if not candidate.exists():
                dst = candidate
                break
            i += 1
    shutil.move(staged, dst)
    return dst


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root)
    queue_host = Path(args.queue_dir_host)
    reject_host = Path(args.reject_dir_host)
    log_path = Path(args.log)

    if not source_root.exists():
        print(f"source root does not exist: {source_root}", file=sys.stderr)
        return 2

    api_key = args.api_key or read_api_key(args.mylar_config)
    exclusions = load_exclusions(args.exclude_csv)
    candidates = build_candidates(source_root, exclusions)
    if args.limit is not None:
        candidates = candidates[: args.limit]

    print(f"source_root={source_root}")
    print(f"candidate_count={len(candidates)}")
    print(f"queue_dir_host={queue_host}")
    print(f"queue_dir_mylar={args.queue_dir_mylar}")
    print(f"mode={args.mode}")
    print(f"cooldown_seconds={args.cooldown_seconds}")
    print(f"timeout_seconds={args.timeout_seconds}")
    print(f"log={log_path}")

    if args.dry_run:
        for path in candidates[:100]:
            print(path)
        return 0

    ensure_empty_dir(queue_host)

    for idx, src in enumerate(candidates, start=1):
        print(f"[{idx}/{len(candidates)}] staging {src}")
        staged = stage_file(src, queue_host, args.mode)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            response = force_process(args.mylar_url, api_key, args.queue_dir_mylar)
            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "source_path": str(src),
                    "staged_path": str(staged),
                    "mode": args.mode,
                    "status": "submitted",
                    "detail": response.strip(),
                },
            )
        except Exception as exc:
            rejected = reject_file(staged, reject_host)
            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "source_path": str(src),
                    "staged_path": str(rejected),
                    "mode": args.mode,
                    "status": "api_error",
                    "detail": str(exc),
                },
            )
            time.sleep(args.cooldown_seconds)
            continue

        consumed = wait_for_consumption(staged, args.timeout_seconds, args.poll_seconds)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        if consumed:
            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "source_path": str(src),
                    "staged_path": str(staged),
                    "mode": args.mode,
                    "status": "consumed",
                    "detail": "Mylar removed staged file from queue dir",
                },
            )
        else:
            rejected = reject_file(staged, reject_host)
            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "source_path": str(src),
                    "staged_path": str(rejected),
                    "mode": args.mode,
                    "status": "timeout_rejected",
                    "detail": f"File still present after {args.timeout_seconds}s",
                },
            )
        time.sleep(args.cooldown_seconds)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
