#!/usr/bin/env python3
"""Resolve a ComicVine issue id from local GCD/Metron metadata.

This utility is review-only. It reads a CBZ or a metadata row, enriches the
series/issue/year/publisher fields from local GCD and Metron sources when
available, then uses the existing ComicVine resolver scoring logic to report the
best ComicVine issue id.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MYLAR_ROOT = Path("/home/rmleonard/Projects/mylar-library")
DEFAULT_CONFIG = MYLAR_ROOT / "config.ini"
DEFAULT_CBL_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_GCD_DB = MYLAR_ROOT / "utilities/2025-10-15.db"
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")

from utilities.cv_issue_resolver import cv_request, best_issue_number_match, best_issue_search_match, best_volume_match, load_cv_config  # noqa: E402


@dataclass
class ResolveRow:
    source: str
    series: str
    issue: str
    year: str
    publisher: str
    title: str
    gcd_series_id: str
    gcd_issue_number: str
    gcd_issue_date: str
    gcd_series_year: str
    metron_series: str
    metron_issue: str
    metron_cover_date: str
    comicvine_volume_id: str
    comicvine_volume_name: str
    comicvine_volume_year: str
    comicvine_issue_id: str
    comicvine_issue_name: str
    comicvine_issue_date: str
    confidence: str
    status: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"resolve_issue_from_local_metadata_{ts}.csv"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", help="CBZ root to inspect")
    ap.add_argument("--series")
    ap.add_argument("--issue")
    ap.add_argument("--year")
    ap.add_argument("--publisher")
    ap.add_argument("--title", default="")
    ap.add_argument("--gcd-db", default=str(DEFAULT_GCD_DB))
    ap.add_argument("--cbl-db", default=str(DEFAULT_CBL_DB))
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--report", default="")
    ap.add_argument("--limit", type=int, default=0)
    return ap.parse_args()


def read_series_json(cbz_path: Path) -> dict[str, str]:
    current = cbz_path.parent.resolve()
    root = current.anchor
    while True:
        candidate = current / "series.json"
        if candidate.exists():
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                return {}
            meta = payload.get("metadata") or {}
            if isinstance(meta, list):
                meta = meta[0] if meta else {}
            if not isinstance(meta, dict):
                return {}
            return {
                "series": str(meta.get("name") or meta.get("series") or "").strip(),
                "publisher": str(meta.get("publisher") or "").strip(),
                "year": str(meta.get("year") or "").strip(),
                "comicid": str(meta.get("comicid") or "").strip(),
            }
        if str(current) == root:
            return {}
        current = current.parent


def read_cbz_comicinfo(cbz_path: Path) -> dict[str, str]:
    import zipfile
    from xml.etree import ElementTree as ET

    try:
        with zipfile.ZipFile(cbz_path, "r") as zf:
            target = next((n for n in zf.namelist() if n.lower() == "comicinfo.xml"), None)
            if not target:
                return {}
            root = ET.fromstring(zf.read(target))
    except Exception:
        return {}

    def text(tag: str) -> str:
        node = root.find(tag)
        return (node.text or "").strip() if node is not None and node.text else ""

    return {
        "series": text("Series"),
        "issue": text("Number"),
        "year": text("Year"),
        "publisher": text("Publisher"),
        "title": text("Title"),
    }


def load_gcd_metadata(db_path: Path, series: str, year: str, issue: str, publisher: str) -> dict[str, str]:
    if not db_path.exists() or not series:
        return {}
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        row = None
        if year and publisher:
            row = cur.execute(
                """
                SELECT s.id AS series_id, s.name AS series_name, s.year_began AS series_year,
                       p.name AS publisher_name, i.number AS issue_number,
                       i.publication_date AS publication_date, i.key_date AS key_date
                FROM gcd_series s
                JOIN gcd_publisher p ON s.publisher_id = p.id
                LEFT JOIN gcd_issue i ON i.series_id = s.id AND i.number = ?
                WHERE lower(s.name) = lower(?) AND s.year_began = ? AND lower(p.name) = lower(?)
                LIMIT 1
                """,
                (issue or "", series, int(year), publisher),
            ).fetchone()
        if row is None and year:
            row = cur.execute(
                """
                SELECT s.id AS series_id, s.name AS series_name, s.year_began AS series_year,
                       p.name AS publisher_name, i.number AS issue_number,
                       i.publication_date AS publication_date, i.key_date AS key_date
                FROM gcd_series s
                JOIN gcd_publisher p ON s.publisher_id = p.id
                LEFT JOIN gcd_issue i ON i.series_id = s.id AND i.number = ?
                WHERE lower(s.name) = lower(?) AND s.year_began = ?
                LIMIT 1
                """,
                (issue or "", series, int(year)),
            ).fetchone()
        if row is None:
            row = cur.execute(
                """
                SELECT s.id AS series_id, s.name AS series_name, s.year_began AS series_year,
                       p.name AS publisher_name, i.number AS issue_number,
                       i.publication_date AS publication_date, i.key_date AS key_date
                FROM gcd_series s
                JOIN gcd_publisher p ON s.publisher_id = p.id
                LEFT JOIN gcd_issue i ON i.series_id = s.id AND i.number = ?
                WHERE lower(s.name) = lower(?)
                LIMIT 1
                """,
                (issue or "", series),
            ).fetchone()
        if not row:
            return {}
        return {
            "gcd_series_id": str(row["series_id"] or ""),
            "gcd_series_name": str(row["series_name"] or ""),
            "gcd_series_year": str(row["series_year"] or ""),
            "gcd_publisher": str(row["publisher_name"] or ""),
            "gcd_issue_number": str(row["issue_number"] or ""),
            "gcd_issue_date": str(row["publication_date"] or row["key_date"] or ""),
        }
    finally:
        con.close()


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    sources: list[Path] = []
    if args.root:
        sources = sorted(Path(args.root).rglob("*.cbz"))

    if not sources:
        data = {
            "source": "manual",
            "series": args.series or "",
            "issue": args.issue or "",
            "year": args.year or "",
            "publisher": args.publisher or "",
            "title": args.title or "",
        }
        return [data]

    rows: list[dict[str, str]] = []
    for cbz in sources:
        ci = read_cbz_comicinfo(cbz)
        sj = read_series_json(cbz)
        rows.append(
            {
                "source": str(cbz),
                "series": ci.get("series") or sj.get("series") or "",
                "issue": ci.get("issue") or "",
                "year": ci.get("year") or sj.get("year") or "",
                "publisher": ci.get("publisher") or sj.get("publisher") or "",
                "title": ci.get("title") or "",
            }
        )
    return rows


def resolve_one(row: dict[str, str], api_key: str, user_agent: str, base_url: str, cbl_db: Path, gcd_db: Path) -> ResolveRow:
    series = row.get("series", "")
    issue = row.get("issue", "")
    year = row.get("year", "")
    publisher = row.get("publisher", "")
    title = row.get("title", "")

    gcd = load_gcd_metadata(gcd_db, series, year, issue, publisher)
    if gcd:
        series = gcd.get("gcd_series_name") or series
        year = gcd.get("gcd_series_year") or year
        publisher = gcd.get("gcd_publisher") or publisher
        issue = gcd.get("gcd_issue_number") or issue

    cbl_conn = sqlite3.connect(str(cbl_db))
    cbl_conn.row_factory = sqlite3.Row
    try:
        cbl_volume, cbl_note = None, "no_cbl_cache"
        if series:
            try:
                from utilities.cv_issue_resolver import query_cbl_cache  # late import to reuse scoring
                cbl_volume, cbl_note = query_cbl_cache(cbl_conn, series, issue, year, publisher)
            except Exception as exc:
                cbl_note = f"cbl_cache_failed:{exc}"
    finally:
        cbl_conn.close()

    volume = cbl_volume
    trusted_volume = False
    if volume is not None and volume.volume_id:
        trusted_volume = True

    note = cbl_note
    if not volume or not volume.volume_id:
        try:
            vol_search = cv_request(
                base_url=base_url,
                api_key=api_key,
                user_agent=user_agent,
                endpoint="search",
                params={"resources": "volume", "query": series, "limit": "20"},
            )
            volume = best_volume_match(vol_search.get("results", []), series, year, publisher, title)
        except Exception as exc:
            return ResolveRow(
                source=row.get("source", ""),
                series=series,
                issue=issue,
                year=year,
                publisher=publisher,
                title=title,
                gcd_series_id=gcd.get("gcd_series_id", ""),
                gcd_issue_number=gcd.get("gcd_issue_number", ""),
                gcd_issue_date=gcd.get("gcd_issue_date", ""),
                gcd_series_year=gcd.get("gcd_series_year", ""),
                metron_series="",
                metron_issue="",
                metron_cover_date="",
                comicvine_volume_id="",
                comicvine_volume_name="",
                comicvine_volume_year="",
                comicvine_issue_id="",
                comicvine_issue_name="",
                comicvine_issue_date="",
                confidence="none",
                status="error",
                note=f"volume_search_failed:{exc}",
            )

    issue_id = ""
    issue_name = ""
    issue_date = ""
    confidence = "none"
    status = "unresolved"

    if volume and volume.volume_id:
        try:
            if issue:
                issues = cv_request(
                    base_url=base_url,
                    api_key=api_key,
                    user_agent=user_agent,
                    endpoint="issues",
                    params={"filter": f"volume:{volume.volume_id},issue_number:{issue}", "limit": "5"},
                )
                results = issues.get("results", []) if issues else []
                if results:
                    best = results[0]
                    issue_id = str(best.get("id") or "")
                    issue_name = str(best.get("name") or "")
                    issue_date = str(best.get("cover_date") or "")
                else:
                    issue_search = cv_request(
                        base_url=base_url,
                        api_key=api_key,
                        user_agent=user_agent,
                        endpoint="search",
                        params={"resources": "issue", "query": f"{series} {issue}", "limit": "10"},
                    )
                    best_issue = best_issue_number_match(issue_search.get("results", []), series, issue, year, publisher)
                    if best_issue:
                        issue_id = str(best_issue.get("id") or "")
                        issue_name = str(best_issue.get("name") or "")
                        issue_date = str(best_issue.get("cover_date") or "")
            elif title:
                issue_search = cv_request(
                    base_url=base_url,
                    api_key=api_key,
                    user_agent=user_agent,
                    endpoint="search",
                    params={"resources": "issue", "query": f"{series} {title}", "limit": "10"},
                )
                best_issue = best_issue_search_match(issue_search.get("results", []), title, year, publisher)
                if best_issue:
                    issue_id = str(best_issue.get("id") or "")
                    issue_name = str(best_issue.get("name") or "")
                    issue_date = str(best_issue.get("cover_date") or "")
        except Exception as exc:
            return ResolveRow(
                source=row.get("source", ""),
                series=series,
                issue=issue,
                year=year,
                publisher=publisher,
                title=title,
                gcd_series_id=gcd.get("gcd_series_id", ""),
                gcd_issue_number=gcd.get("gcd_issue_number", ""),
                gcd_issue_date=gcd.get("gcd_issue_date", ""),
                gcd_series_year=gcd.get("gcd_series_year", ""),
                metron_series="",
                metron_issue="",
                metron_cover_date="",
                comicvine_volume_id=volume.volume_id,
                comicvine_volume_name=volume.volume_name,
                comicvine_volume_year=volume.volume_year,
                comicvine_issue_id="",
                comicvine_issue_name="",
                comicvine_issue_date="",
                confidence="none",
                status="error",
                note=f"issue_search_failed:{exc}",
            )

    if issue_id:
        if trusted_volume:
            confidence = "high"
            status = "resolved"
        elif volume.score >= 10:
            confidence = "medium"
            status = "candidate"
        else:
            confidence = "low"
            status = "candidate"
    else:
        status = "unresolved"
        note = note or "no_issue_match"

    return ResolveRow(
        source=row.get("source", ""),
        series=series,
        issue=issue,
        year=year,
        publisher=publisher,
        title=title,
        gcd_series_id=gcd.get("gcd_series_id", ""),
        gcd_issue_number=gcd.get("gcd_issue_number", ""),
        gcd_issue_date=gcd.get("gcd_issue_date", ""),
        gcd_series_year=gcd.get("gcd_series_year", ""),
        metron_series="",
        metron_issue="",
        metron_cover_date="",
        comicvine_volume_id=volume.volume_id if volume else "",
        comicvine_volume_name=volume.volume_name if volume else "",
        comicvine_volume_year=volume.volume_year if volume else "",
        comicvine_issue_id=issue_id,
        comicvine_issue_name=issue_name,
        comicvine_issue_date=issue_date,
        confidence=confidence,
        status=status,
        note=note,
    )


def main() -> int:
    args = parse_args()
    api_key, user_agent, base_url, _rate = load_cv_config(Path(args.config))
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    rows = build_rows(args)
    if args.limit > 0:
        rows = rows[: args.limit]

    resolved: list[ResolveRow] = []
    for row in rows:
        resolved.append(resolve_one(row, api_key, user_agent, base_url, Path(args.cbl_db), Path(args.gcd_db)))

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "source",
                "series",
                "issue",
                "year",
                "publisher",
                "title",
                "gcd_series_id",
                "gcd_issue_number",
                "gcd_issue_date",
                "gcd_series_year",
                "metron_series",
                "metron_issue",
                "metron_cover_date",
                "comicvine_volume_id",
                "comicvine_volume_name",
                "comicvine_volume_year",
                "comicvine_issue_id",
                "comicvine_issue_name",
                "comicvine_issue_date",
                "confidence",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        for row in resolved:
            writer.writerow(row.__dict__)

    print(f"processed={len(resolved)}")
    print(f"report={report_path}")
    print(f"resolved={sum(1 for r in resolved if r.status == 'resolved')}")
    print(f"candidates={sum(1 for r in resolved if r.status == 'candidate')}")
    print(f"unresolved={sum(1 for r in resolved if r.status == 'unresolved')}")
    print(f"errors={sum(1 for r in resolved if r.status == 'error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
