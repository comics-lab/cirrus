#!/usr/bin/env python3
"""Series-aware Mylar importer for pre-organized library trees.

This importer is for source trees where each series directory already carries a
usable ComicVine volume id in `series.json` or `cvinfo`. It adds each series to
Mylar, copies the `.cbz` files into the watched series folder, then asks Mylar
to rescan and rename that series.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import os
import shutil
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_MYlar_URL = "http://192.168.1.113:8090"
DEFAULT_CONFIG = "/mnt/phoenix/services/mylar/mylar/config.ini"
DEFAULT_DB = "/mnt/phoenix/services/mylar/mylar/mylar.db"
DEFAULT_COMICS_HOST_ROOT = "/mnt/phoenix/media/comics"
DEFAULT_LOG = "/tmp/mylar_series_import.csv"
DEFAULT_SKIP_KEYWORDS = (
    "annual",
    "digest",
    "double digest",
    "jumbo",
    "one-shot",
    "one shot",
    "special",
    "spectacular",
    "tpb",
    "collection",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import series-aware pre-tagged `.cbz` directories into Mylar."
    )
    parser.add_argument("--source-root", required=True, help="Root containing series directories")
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
        "--db-path",
        default=DEFAULT_DB,
        help=f"Mylar database path (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--comics-host-root",
        default=DEFAULT_COMICS_HOST_ROOT,
        help=f"Host path backing Mylar /comics (default: {DEFAULT_COMICS_HOST_ROOT})",
    )
    parser.add_argument(
        "--log",
        default=DEFAULT_LOG,
        help=f"CSV log path (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional max number of series directories to process",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=2.0,
        help="Sleep between series-level API steps (default: 2.0)",
    )
    parser.add_argument(
        "--settle-seconds",
        type=float,
        default=8.0,
        help="Wait after recheckFiles before manualRename (default: 8.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned work without changing Mylar or copying files",
    )
    parser.add_argument(
        "--include-special-formats",
        action="store_true",
        help="Include annual/digest/special-format directories instead of skipping them by default",
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


def read_series_json(series_dir: Path) -> tuple[str | None, str]:
    series_json = series_dir / "series.json"
    if not series_json.exists():
        return None, "missing_series_json"
    try:
        payload = json.loads(series_json.read_text())
    except Exception as exc:
        return None, f"bad_series_json:{exc}"
    metadata = payload.get("metadata") or {}
    comicid = metadata.get("comicid")
    if comicid is None:
        return None, "missing_comicid"
    return str(comicid).strip(), "ok"


def classify_series_dir(series_dir: Path, include_special_formats: bool) -> tuple[bool, str]:
    if include_special_formats:
        return True, "plain_or_allowed"
    name = series_dir.name.lower()
    for token in DEFAULT_SKIP_KEYWORDS:
        if token in name:
            return False, f"special_format:{token}"
    return True, "plain_series"


def discover_series_dirs(
    source_root: Path, include_special_formats: bool
) -> tuple[list[Path], list[tuple[Path, str]]]:
    series_dirs: list[Path] = []
    skipped: list[tuple[Path, str]] = []
    for path in sorted(source_root.rglob("series.json")):
        series_dir = path.parent
        if any(series_dir.glob("*.cbz")):
            allowed, reason = classify_series_dir(series_dir, include_special_formats)
            if allowed:
                series_dirs.append(series_dir)
            else:
                skipped.append((series_dir, reason))
    return series_dirs, skipped


def call_api(mylar_url: str, api_key: str, cmd: str, **params: str) -> str:
    query = {"apikey": api_key, "cmd": cmd}
    query.update(params)
    url = f"{mylar_url.rstrip('/')}/api?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def call_web(mylar_url: str, path: str, **params: str) -> str:
    url = f"{mylar_url.rstrip('/')}/{path.lstrip('/')}?{urllib.parse.urlencode(params, doseq=True)}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def db_connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def fetch_comic_record(con: sqlite3.Connection, comicid: str):
    deadline = time.time() + 30
    while True:
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT ComicID, ComicName, ComicLocation, Total, Have FROM comics WHERE ComicID = ?",
                (comicid,),
            )
            return cur.fetchone()
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or time.time() >= deadline:
                raise
            time.sleep(1)


def fetch_existing_comic_ids(con: sqlite3.Connection) -> set[str]:
    deadline = time.time() + 30
    while True:
        try:
            cur = con.cursor()
            cur.execute("SELECT ComicID FROM comics")
            return {str(row[0]) for row in cur.fetchall()}
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or time.time() >= deadline:
                raise
            time.sleep(1)


def wait_for_comic_record(con: sqlite3.Connection, comicid: str, timeout_seconds: int = 120):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        row = fetch_comic_record(con, comicid)
        if row and row["ComicLocation"]:
            return row
        time.sleep(2)
    return fetch_comic_record(con, comicid)


def to_host_comics_path(comic_location: str, host_root: Path) -> Path:
    prefix = "/comics/"
    if not comic_location.startswith(prefix):
        raise RuntimeError(f"Unexpected ComicLocation outside /comics: {comic_location}")
    rel = comic_location[len(prefix) :]
    return host_root / rel


def copy_issue_files(series_dir: Path, dest_dir: Path) -> tuple[int, int, list[str]]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    skipped = 0
    errors: list[str] = []
    for src in sorted(series_dir.glob("*.cbz")):
        dst = dest_dir / src.name
        if dst.exists():
            skipped += 1
            continue
        try:
            shutil.copy2(src, dst)
            copied += 1
        except Exception as exc:
            errors.append(f"{src.name}:{exc}")
    return copied, skipped, errors


def append_log(log_path: Path, row: dict[str, str]) -> None:
    exists = log_path.exists()
    with log_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "series_dir",
                "comicid",
                "comic_name",
                "comic_location",
                "files_copied",
                "files_skipped",
                "status",
                "detail",
            ],
        )
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root)
    db_path = Path(args.db_path)
    comics_host_root = Path(args.comics_host_root)
    log_path = Path(args.log)

    if not source_root.exists():
        print(f"source root does not exist: {source_root}", file=sys.stderr)
        return 2

    api_key = args.api_key or read_api_key(args.mylar_config)
    series_dirs, skipped_series_dirs = discover_series_dirs(
        source_root, args.include_special_formats
    )
    con = db_connect(db_path)
    existing_comicids = fetch_existing_comic_ids(con)
    filtered_series_dirs: list[Path] = []
    for series_dir in series_dirs:
        comicid, status = read_series_json(series_dir)
        if not comicid:
            filtered_series_dirs.append(series_dir)
            continue
        if comicid in existing_comicids:
            skipped_series_dirs.append((series_dir, "already_in_mylar"))
            continue
        filtered_series_dirs.append(series_dir)
    series_dirs = filtered_series_dirs
    if args.limit is not None:
        series_dirs = series_dirs[: args.limit]

    print(f"source_root={source_root}")
    print(f"series_dir_count={len(series_dirs)}")
    print(f"skipped_series_dir_count={len(skipped_series_dirs)}")
    print(f"log={log_path}")

    if args.dry_run:
        for series_dir, reason in skipped_series_dirs[:100]:
            print(f"SKIP {series_dir} reason={reason}")
        for series_dir in series_dirs:
            comicid, status = read_series_json(series_dir)
            print(f"{series_dir} comicid={comicid} status={status}")
        return 0

    try:
        for series_dir, reason in skipped_series_dirs:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "series_dir": str(series_dir),
                    "comicid": "",
                    "comic_name": "",
                    "comic_location": "",
                    "files_copied": "0",
                    "files_skipped": "0",
                    "status": "skip",
                    "detail": reason,
                },
            )
        for idx, series_dir in enumerate(series_dirs, start=1):
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            comicid, status = read_series_json(series_dir)
            if not comicid:
                append_log(
                    log_path,
                    {
                        "timestamp": ts,
                        "series_dir": str(series_dir),
                        "comicid": "",
                        "comic_name": "",
                        "comic_location": "",
                        "files_copied": "0",
                        "files_skipped": "0",
                        "status": "skip",
                        "detail": status,
                    },
                )
                print(f"[{idx}/{len(series_dirs)}] skip {series_dir} {status}")
                continue

            print(f"[{idx}/{len(series_dirs)}] add/reconcile comicid={comicid} series_dir={series_dir}")
            try:
                add_response = call_api(args.mylar_url, api_key, "addComic", id=comicid)
            except Exception as exc:
                append_log(
                    log_path,
                    {
                        "timestamp": ts,
                        "series_dir": str(series_dir),
                        "comicid": comicid,
                        "comic_name": "",
                        "comic_location": "",
                        "files_copied": "0",
                        "files_skipped": "0",
                        "status": "error",
                        "detail": f"addComic:{exc}",
                    },
                )
                continue

            time.sleep(args.delay_seconds)
            row = wait_for_comic_record(con, comicid)
            if not row or not row["ComicLocation"]:
                append_log(
                    log_path,
                    {
                        "timestamp": ts,
                        "series_dir": str(series_dir),
                        "comicid": comicid,
                        "comic_name": "",
                        "comic_location": "",
                        "files_copied": "0",
                        "files_skipped": "0",
                        "status": "error",
                        "detail": f"missing_comiclocation add_response={add_response[:120]}",
                    },
                )
                continue

            host_dest = to_host_comics_path(row["ComicLocation"], comics_host_root)
            copied, skipped, copy_errors = copy_issue_files(series_dir, host_dest)

            try:
                call_api(args.mylar_url, api_key, "recheckFiles", id=comicid)
                time.sleep(args.settle_seconds)
                call_web(args.mylar_url, "manualRename", comicid=comicid)
                if copy_errors:
                    detail = "recheckFiles+manualRename copy_errors=" + " | ".join(copy_errors[:10])
                    status_value = "partial"
                else:
                    detail = "recheckFiles+manualRename"
                    status_value = "ok"
            except Exception as exc:
                if copy_errors:
                    detail = f"post_copy_api:{exc} copy_errors=" + " | ".join(copy_errors[:10])
                else:
                    detail = f"post_copy_api:{exc}"
                status_value = "error"

            append_log(
                log_path,
                {
                    "timestamp": ts,
                    "series_dir": str(series_dir),
                    "comicid": comicid,
                    "comic_name": str(row["ComicName"] or ""),
                    "comic_location": str(row["ComicLocation"] or ""),
                    "files_copied": str(copied),
                    "files_skipped": str(skipped),
                    "status": status_value,
                    "detail": detail,
                },
            )
            time.sleep(args.delay_seconds)
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
