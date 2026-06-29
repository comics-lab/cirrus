#!/usr/bin/env python3
"""Report reading-list matches against the local CBL ComicVine cache."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/home/rmleonard/Projects/CBL-ReadingLists")
DEFAULT_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")


@dataclass
class MatchRow:
    list_path: str
    list_name: str
    book_index: int
    series: str
    number: str
    volume: str
    year: str
    comicvine_series_id: str
    comicvine_issue_id: str
    match_status: str
    match_count: int


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"cbl_cache_match_report_{ts}.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory containing .cbl files")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite cache path")
    parser.add_argument("--report", default="", help="Optional CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of books to inspect")
    return parser.parse_args()


def parse_cbl(path: Path) -> tuple[str, list[dict[str, str]]]:
    tree = ET.parse(path)
    root = tree.getroot()
    list_name = (root.findtext("Name") or "").strip()
    rows: list[dict[str, str]] = []
    books = root.find("Books")
    if books is None:
        return list_name, rows
    for idx, book in enumerate(books.findall("Book"), start=1):
        db = book.find("Database")
        if db is None or (db.attrib.get("Name") or "").strip().casefold() != "cv":
            continue
        rows.append(
            {
                "book_index": str(idx),
                "series": (book.attrib.get("Series") or "").strip(),
                "number": (book.attrib.get("Number") or "").strip(),
                "volume": (book.attrib.get("Volume") or "").strip(),
                "year": (book.attrib.get("Year") or "").strip(),
                "comicvine_series_id": (db.attrib.get("Series") or "").strip(),
                "comicvine_issue_id": (db.attrib.get("Issue") or "").strip(),
            }
        )
    return list_name, rows


def load_cache(conn: sqlite3.Connection, series: str):
    return conn.execute(
        """
        SELECT series, number, volume, year, comicvine_series_id, comicvine_issue_id
        FROM cbl_issue_lookup
        WHERE lower(series) = lower(?)
           OR lower(series) LIKE lower(?)
        """,
        (series, f"%{series}%"),
    ).fetchall()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    db_path = Path(args.db).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows: list[MatchRow] = []
    stats = Counter()
    per_list = defaultdict(Counter)
    processed = 0

    try:
        for cbl_path in sorted(root.rglob("*.cbl")):
            list_name, books = parse_cbl(cbl_path)
            for book in books:
                if args.limit and processed >= args.limit:
                    break
                processed += 1
                series = book["series"]
                number = book["number"]
                year = book["year"]
                publisher = ""
                cache_rows = load_cache(conn, series) if series else []
                match_status = "unmatched"
                match_count = len(cache_rows)
                if cache_rows:
                    exact = [r for r in cache_rows if str(r["number"]).strip() == number]
                    if exact:
                        match_status = "exact"
                    elif len(cache_rows) == 1:
                        match_status = "series_only"
                    else:
                        match_status = "ambiguous"

                stats[match_status] += 1
                per_list[list_name][match_status] += 1
                chosen = cache_rows[0] if cache_rows else None
                rows.append(
                    MatchRow(
                        list_path=str(cbl_path),
                        list_name=list_name,
                        book_index=int(book["book_index"]),
                        series=series,
                        number=number,
                        volume=book["volume"],
                        year=year,
                        comicvine_series_id=str(chosen["comicvine_series_id"]).strip() if chosen else "",
                        comicvine_issue_id=str(chosen["comicvine_issue_id"]).strip() if chosen else "",
                        match_status=match_status,
                        match_count=match_count,
                    )
                )
            if args.limit and processed >= args.limit:
                break
    finally:
        conn.close()

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
                "comicvine_series_id",
                "comicvine_issue_id",
                "match_status",
                "match_count",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    print(f"scan_root={root}")
    print(f"db={db_path}")
    print(f"report={report_path}")
    print(f"processed={processed}")
    print(f"match_counts={dict(stats)}")
    print("per_list=")
    for name in sorted(per_list):
        print(f"  {name}: {dict(per_list[name])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
