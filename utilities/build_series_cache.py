#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path


DEFAULT_OUTPUT = "/home/rmleonard/Projects/cirrus/data/series_cache.sqlite3"
DEFAULT_ROOTS = [
    "/mnt/phoenix/media/comics",
    "/mnt/phoenix/media/incoming/grackle-ssh/LIBRARY",
    "/mnt/phoenix/media/incoming/fearless-ssh/LIBRARY",
    "/mnt/grackle/LIBRARY",
    "/mnt/fearless/LIBRARY",
]


def normalize_text(value: str | None) -> str:
    s = (value or "").strip().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build a local SQLite cache of series.json/cvinfo sidecars.")
    ap.add_argument("--output", default=DEFAULT_OUTPUT, help="SQLite database path to write")
    ap.add_argument(
        "--roots",
        nargs="*",
        default=DEFAULT_ROOTS,
        help="Roots to scan for series.json files",
    )
    return ap.parse_args()


def load_series_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    meta = data.get("metadata")
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, list) and meta:
        first = meta[0]
        if isinstance(first, dict):
            return first
    return None


def read_cvinfo(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip() or None
    except Exception:
        return None


def init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS series_cache (
            id INTEGER PRIMARY KEY,
            source_root TEXT NOT NULL,
            series_dir TEXT NOT NULL,
            publisher TEXT,
            publisher_norm TEXT,
            series_name TEXT,
            series_name_norm TEXT,
            comicvine_volume_id INTEGER,
            start_year INTEGER,
            imprint TEXT,
            booktype TEXT,
            age_rating TEXT,
            issue_count INTEGER,
            publication_run TEXT,
            cvinfo TEXT,
            series_json_path TEXT NOT NULL,
            cvinfo_path TEXT,
            UNIQUE(series_dir)
        );
        CREATE INDEX IF NOT EXISTS idx_series_cache_name ON series_cache(series_name_norm);
        CREATE INDEX IF NOT EXISTS idx_series_cache_pub_name ON series_cache(publisher_norm, series_name_norm);
        CREATE INDEX IF NOT EXISTS idx_series_cache_cv ON series_cache(comicvine_volume_id);
        """
    )
    con.commit()


def insert_rows(con: sqlite3.Connection, rows: list[dict]) -> None:
    cur = con.cursor()
    cur.execute("DELETE FROM series_cache")
    cur.executemany(
        """
        INSERT INTO series_cache (
            source_root, series_dir, publisher, publisher_norm, series_name, series_name_norm,
            comicvine_volume_id, start_year, imprint, booktype, age_rating, issue_count,
            publication_run, cvinfo, series_json_path, cvinfo_path
        ) VALUES (
            :source_root, :series_dir, :publisher, :publisher_norm, :series_name, :series_name_norm,
            :comicvine_volume_id, :start_year, :imprint, :booktype, :age_rating, :issue_count,
            :publication_run, :cvinfo, :series_json_path, :cvinfo_path
        )
        """,
        rows,
    )
    con.commit()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    seen_dirs: set[str] = set()

    for root_str in args.roots:
        root = Path(root_str)
        if not root.exists():
            continue
        for series_json in root.rglob("series.json"):
            series_dir = series_json.parent.resolve()
            series_dir_str = str(series_dir)
            if series_dir_str in seen_dirs:
                continue
            seen_dirs.add(series_dir_str)

            meta = load_series_json(series_json)
            if not meta:
                continue

            publisher = meta.get("publisher")
            name = meta.get("name")
            comicid = meta.get("comicid")
            year = meta.get("year")
            cvinfo_path = series_dir / "cvinfo"

            rows.append(
                {
                    "source_root": str(root.resolve()),
                    "series_dir": series_dir_str,
                    "publisher": publisher,
                    "publisher_norm": normalize_text(publisher),
                    "series_name": name,
                    "series_name_norm": normalize_text(name),
                    "comicvine_volume_id": int(comicid) if comicid not in (None, "") else None,
                    "start_year": int(year) if year not in (None, "") else None,
                    "imprint": meta.get("imprint"),
                    "booktype": meta.get("booktype"),
                    "age_rating": meta.get("age_rating"),
                    "issue_count": int(meta.get("total_issues")) if meta.get("total_issues") not in (None, "") else None,
                    "publication_run": meta.get("publication_run"),
                    "cvinfo": read_cvinfo(cvinfo_path),
                    "series_json_path": str(series_json.resolve()),
                    "cvinfo_path": str(cvinfo_path.resolve()) if cvinfo_path.exists() else None,
                }
            )

    con = sqlite3.connect(output)
    try:
        init_db(con)
        insert_rows(con, rows)
    finally:
        con.close()

    print(f"output={output}")
    print(f"series_rows={len(rows)}")
    print(f"roots_scanned={len(args.roots)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
