#!/usr/bin/env python3
"""Build a local ComicVine lookup cache from CBL reading lists.

This scans `.cbl` files under a source tree and extracts ComicVine-backed
issue references from each `<Book>` entry.

The resulting SQLite cache is intended to accelerate local metadata matching
and Pass 1 lookup work without repeatedly re-reading the source XML files.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/home/rmleonard/Projects/CBL-ReadingLists")
DEFAULT_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")


@dataclass
class CblRow:
    list_path: str
    list_name: str
    book_index: int
    series: str
    number: str
    volume: str
    year: str
    db_name: str
    comicvine_series_id: str
    comicvine_issue_id: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"cbl_cache_{ts}.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory containing .cbl files")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite cache path")
    parser.add_argument("--report", default="", help="Optional CSV report path")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing the database")
    return parser.parse_args()


def parse_cbl(path: Path) -> list[CblRow]:
    tree = ET.parse(path)
    root = tree.getroot()
    list_name = (root.findtext("Name") or "").strip()
    rows: list[CblRow] = []
    books = root.find("Books")
    if books is None:
        return rows

    for idx, book in enumerate(books.findall("Book"), start=1):
        db = book.find("Database")
        if db is None:
            continue
        db_name = (db.attrib.get("Name") or "").strip()
        if db_name.casefold() != "cv":
            continue
        rows.append(
            CblRow(
                list_path=str(path),
                list_name=list_name,
                book_index=idx,
                series=(book.attrib.get("Series") or "").strip(),
                number=(book.attrib.get("Number") or "").strip(),
                volume=(book.attrib.get("Volume") or "").strip(),
                year=(book.attrib.get("Year") or "").strip(),
                db_name=db_name,
                comicvine_series_id=(db.attrib.get("Series") or "").strip(),
                comicvine_issue_id=(db.attrib.get("Issue") or "").strip(),
            )
        )
    return rows


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;

        CREATE TABLE IF NOT EXISTS cbl_issue_lookup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_path TEXT NOT NULL,
            list_name TEXT NOT NULL,
            book_index INTEGER NOT NULL,
            series TEXT NOT NULL,
            number TEXT NOT NULL,
            volume TEXT NOT NULL,
            year TEXT NOT NULL,
            db_name TEXT NOT NULL,
            comicvine_series_id TEXT NOT NULL,
            comicvine_issue_id TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cbl_series ON cbl_issue_lookup(series);
        CREATE INDEX IF NOT EXISTS idx_cbl_issue ON cbl_issue_lookup(number);
        CREATE INDEX IF NOT EXISTS idx_cbl_cv_issue ON cbl_issue_lookup(comicvine_issue_id);
        CREATE INDEX IF NOT EXISTS idx_cbl_cv_series ON cbl_issue_lookup(comicvine_series_id);
        """
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    db_path = Path(args.db).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    rows: list[CblRow] = []
    failures: list[tuple[str, str]] = []

    for cbl_path in sorted(root.rglob("*.cbl")):
        try:
            rows.extend(parse_cbl(cbl_path))
        except Exception as exc:
            failures.append((str(cbl_path), str(exc)))

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "list_path",
                "list_name",
                "book_index",
                "series",
                "number",
                "volume",
                "year",
                "db_name",
                "comicvine_series_id",
                "comicvine_issue_id",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    if args.dry_run:
        print(f"scan_root={root}")
        print(f"report={report_path}")
        print(f"rows={len(rows)} failures={len(failures)}")
        return 0

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        init_db(conn)
        conn.execute("DELETE FROM cbl_issue_lookup")
        conn.executemany(
            """
            INSERT INTO cbl_issue_lookup (
                list_path, list_name, book_index, series, number, volume, year,
                db_name, comicvine_series_id, comicvine_issue_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.list_path,
                    row.list_name,
                    row.book_index,
                    row.series,
                    row.number,
                    row.volume,
                    row.year,
                    row.db_name,
                    row.comicvine_series_id,
                    row.comicvine_issue_id,
                )
                for row in rows
            ],
        )
        conn.commit()
    finally:
        conn.close()

    print(f"scan_root={root}")
    print(f"db={db_path}")
    print(f"report={report_path}")
    print(f"rows={len(rows)} failures={len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
