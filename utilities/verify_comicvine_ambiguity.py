#!/usr/bin/env python3
"""Verify ambiguous ComicVine issue ids against ComicVine metadata.

Review-only utility. It reads ambiguous issue ids from the local cache, queries
ComicVine at a throttled pace, and writes a comparison report. It does not
modify the cache or any source files.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_CONFIG = Path("/home/rmleonard/Projects/mylar-library/config.ini")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")
DEFAULT_AMBIGUOUS_APPENDIX = Path("/home/rmleonard/Projects/cirrus/docs/cbl-cache-ambiguous-comicvine-ids.md")


@dataclass
class VerifyRow:
    comicvine_issue_id: str
    cache_rows: int
    variants: int
    series_count: int
    number_count: int
    year_count: int
    cache_serieses: str
    cache_numbers: str
    cache_years: str
    api_issue_name: str
    api_issue_number: str
    api_issue_date: str
    api_volume_id: str
    api_volume_name: str
    api_volume_year: str
    api_publisher: str
    best_cache_series: str
    best_cache_number: str
    best_cache_year: str
    best_cache_volume: str
    status: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"verify_comicvine_ambiguity_{ts}.csv"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--report", default="")
    ap.add_argument("--limit", type=int, default=0, help="Optional maximum ids to verify")
    ap.add_argument("--delay-seconds", type=float, default=2.0, help="Pause between ComicVine requests")
    ap.add_argument("--appendix", default=str(DEFAULT_AMBIGUOUS_APPENDIX), help="Optional appendix markdown to read ids from")
    return ap.parse_args()


def load_cv_config(path: Path) -> tuple[str, str, str, float]:
    cp = configparser.ConfigParser()
    cp.read(path)
    api_key = cp.get("CV", "comicvine_api", fallback="").strip()
    user_agent = cp.get("CV", "cv_user_agent", fallback="cirrus").strip() or "cirrus"
    base_url = cp.get("CV", "comicvine_url", fallback="https://comicvine.gamespot.com/api/").strip()
    rate = cp.getfloat("CV", "cvapi_rate", fallback=2.0)
    if not api_key:
        raise RuntimeError(f"ComicVine API key not found in {path}")
    return api_key, user_agent, base_url.rstrip("/"), rate


def cv_request(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    endpoint: str,
    params: dict[str, str],
    retries: int = 4,
    backoff: float = 20.0,
) -> dict:
    query = dict(params)
    query.update({"api_key": api_key, "format": "json"})
    url = f"{base_url}/{endpoint.strip('/')}/?{urllib.parse.urlencode(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code in {420, 429} and attempt < retries:
                time.sleep(backoff)
                continue
            raise


def read_ambiguous_ids(db_path: Path) -> list[tuple[str, int, int, int, int, int, str, str, str]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT comicvine_issue_id,
                   COUNT(*) AS rows,
                   COUNT(DISTINCT series || '|' || number || '|' || year) AS variants,
                   COUNT(DISTINCT series) AS series_count,
                   COUNT(DISTINCT number) AS number_count,
                   COUNT(DISTINCT year) AS year_count,
                   GROUP_CONCAT(DISTINCT series) AS serieses,
                   GROUP_CONCAT(DISTINCT number) AS numbers,
                   GROUP_CONCAT(DISTINCT year) AS years
            FROM cbl_issue_lookup
            GROUP BY comicvine_issue_id
            HAVING COUNT(DISTINCT series || '|' || number || '|' || year) > 1
            ORDER BY variants DESC, rows DESC, comicvine_issue_id
            """
        )
        return [tuple(row) for row in cur.fetchall()]
    finally:
        conn.close()


def top_cache_match(db_path: Path, comicvine_issue_id: str) -> tuple[str, str, str, str]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT series, number, volume, year, COUNT(*) AS c
            FROM cbl_issue_lookup
            WHERE comicvine_issue_id = ?
            GROUP BY series, number, volume, year
            ORDER BY c DESC, series, number, year
            LIMIT 1
            """,
            (comicvine_issue_id,),
        )
        row = cur.fetchone()
        if not row:
            return "", "", "", ""
        return str(row["series"]), str(row["number"]), str(row["year"]), str(row["volume"])
    finally:
        conn.close()


def parse_comicvine_appendix(path: Path) -> list[str]:
    if not path.exists():
        return []
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| "):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 3 or parts[1] == "---" or parts[1] == "#":
            continue
        if parts[1].isdigit():
            ids.append(parts[2] if len(parts) > 2 else parts[1])
    return ids


def main() -> int:
    args = parse_args()
    api_key, user_agent, base_url, default_rate = load_cv_config(Path(args.config))
    rate = args.delay_seconds if args.delay_seconds > 0 else default_rate
    db_path = Path(args.db).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    ids = [row[0] for row in read_ambiguous_ids(db_path)]
    if not ids:
        ids = parse_comicvine_appendix(Path(args.appendix))
    if args.limit > 0:
        ids = ids[: args.limit]

    rows: list[VerifyRow] = []
    for idx, comicvine_issue_id in enumerate(ids, start=1):
        cache_rows = variants = series_count = number_count = year_count = 0
        serieses = numbers = years = ""
        # pull cache summary for this id
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(*) AS rows,
                       COUNT(DISTINCT series || '|' || number || '|' || year) AS variants,
                       COUNT(DISTINCT series) AS series_count,
                       COUNT(DISTINCT number) AS number_count,
                       COUNT(DISTINCT year) AS year_count,
                       GROUP_CONCAT(DISTINCT series) AS serieses,
                       GROUP_CONCAT(DISTINCT number) AS numbers,
                       GROUP_CONCAT(DISTINCT year) AS years
                FROM cbl_issue_lookup
                WHERE comicvine_issue_id = ?
                """,
                (comicvine_issue_id,),
            )
            row = cur.fetchone()
            if row:
                cache_rows = int(row["rows"] or 0)
                variants = int(row["variants"] or 0)
                series_count = int(row["series_count"] or 0)
                number_count = int(row["number_count"] or 0)
                year_count = int(row["year_count"] or 0)
                serieses = str(row["serieses"] or "")
                numbers = str(row["numbers"] or "")
                years = str(row["years"] or "")
        finally:
            conn.close()

        best_series, best_number, best_year, best_volume = top_cache_match(db_path, comicvine_issue_id)
        api_issue_name = ""
        api_issue_number = ""
        api_issue_date = ""
        api_volume_id = ""
        api_volume_name = ""
        api_volume_year = ""
        api_publisher = ""
        status = "ok"
        note = ""

        try:
            issue = cv_request(
                base_url=base_url,
                api_key=api_key,
                user_agent=user_agent,
                endpoint=f"issue/4000-{comicvine_issue_id}",
                params={},
            ).get("results") or {}
            api_issue_name = str(issue.get("name") or "")
            api_issue_number = str(issue.get("issue_number") or "")
            api_issue_date = str(issue.get("cover_date") or "")
            volume = issue.get("volume") or {}
            api_volume_id = str(volume.get("id") or "")
            api_volume_name = str(volume.get("name") or "")
            api_volume_year = str(volume.get("start_year") or "")
            publisher = issue.get("publisher") or {}
            api_publisher = str(publisher.get("name") or "")

            if not api_issue_name:
                status = "empty_issue"
                note = "no_issue_name_from_api"
            elif api_issue_number and best_number and api_issue_number != best_number:
                status = "mismatch"
                note = "api_number_differs_from_cache_sample"
            elif api_volume_name and best_series and api_volume_name.casefold() != best_series.casefold():
                status = "mismatch"
                note = "api_volume_differs_from_cache_sample"
        except Exception as exc:
            status = "error"
            note = str(exc)

        rows.append(
            VerifyRow(
                comicvine_issue_id=comicvine_issue_id,
                cache_rows=cache_rows,
                variants=variants,
                series_count=series_count,
                number_count=number_count,
                year_count=year_count,
                cache_serieses=serieses,
                cache_numbers=numbers,
                cache_years=years,
                api_issue_name=api_issue_name,
                api_issue_number=api_issue_number,
                api_issue_date=api_issue_date,
                api_volume_id=api_volume_id,
                api_volume_name=api_volume_name,
                api_volume_year=api_volume_year,
                api_publisher=api_publisher,
                best_cache_series=best_series,
                best_cache_number=best_number,
                best_cache_year=best_year,
                best_cache_volume=best_volume,
                status=status,
                note=note,
            )
        )
        print(f"[{idx}/{len(ids)}] {comicvine_issue_id} {status} {api_volume_name} {api_issue_name}")
        time.sleep(rate)

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "comicvine_issue_id",
                "cache_rows",
                "variants",
                "series_count",
                "number_count",
                "year_count",
                "cache_serieses",
                "cache_numbers",
                "cache_years",
                "api_issue_name",
                "api_issue_number",
                "api_issue_date",
                "api_volume_id",
                "api_volume_name",
                "api_volume_year",
                "api_publisher",
                "best_cache_series",
                "best_cache_number",
                "best_cache_year",
                "best_cache_volume",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    print(f"scan_ids={len(ids)}")
    print(f"report={report_path}")
    print(f"delay_seconds={rate}")
    print(f"ok={sum(1 for r in rows if r.status == 'ok')}")
    print(f"mismatch={sum(1 for r in rows if r.status == 'mismatch')}")
    print(f"error={sum(1 for r in rows if r.status == 'error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
