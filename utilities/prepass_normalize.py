#!/usr/bin/env python3
"""Pre-pass normalization for CBZ files using local sidecars and cache data."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_CACHE_DB = Path("/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")


@dataclass
class PrepassRow:
    cbz_path: str
    series_guess: str
    issue_guess: str
    year_guess: str
    publisher_guess: str
    cache_status: str
    match_series: str
    match_issue_id: str
    match_series_id: str
    action: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"prepass_normalize_{ts}.csv"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--cache-db", default=str(DEFAULT_CACHE_DB))
    ap.add_argument("--report", default="")
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def normalize_lookup_key(value: str) -> str:
    value = (value or "").strip().casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def read_root_comicinfo(cbz: Path) -> dict[str, str]:
    try:
        with zipfile.ZipFile(cbz, "r") as zf:
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
        "number": text("Number"),
        "year": text("Year"),
        "publisher": text("Publisher"),
        "web": text("Web"),
        "notes": text("Notes"),
    }


def read_series_json(cbz: Path) -> dict[str, str]:
    current = cbz.parent.resolve()
    root = current.anchor
    while True:
        candidate = current / "series.json"
        if candidate.exists():
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                return {}
            meta = payload.get("metadata", {})
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


def parse_issue_guess(cbz: Path, root_meta: dict[str, str]) -> str:
    if root_meta.get("number"):
        return root_meta["number"]
    stem = cbz.stem
    m = re.search(r"#?\s*0*([0-9]+[A-Za-z]?)", stem)
    return m.group(1) if m else "1"


def query_cache(conn: sqlite3.Connection | None, series: str, issue: str, year: str, publisher: str):
    if conn is None or not series:
        return None, "no_cache"
    rows = conn.execute(
        """
        SELECT series, number, volume, year, comicvine_series_id, comicvine_issue_id
        FROM cbl_issue_lookup
        WHERE lower(series) = lower(?)
           OR lower(series) LIKE lower(?)
        """,
        (series, f"%{series}%"),
    ).fetchall()
    if not rows:
        return None, "no_cache_match"
    for row in rows:
        if issue and str(row["number"]).strip() == issue:
            return row, "issue_match"
    if len(rows) == 1:
        return rows[0], "unique_series"
    return None, "ambiguous"


def build_comicinfo(series: str, issue: str, year: str, publisher: str, volume: str, notes: str, web: str, comicvine_issue_id: str) -> bytes:
    root = ET.Element("ComicInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or value == "":
            return
        ET.SubElement(root, tag).text = str(value)

    add("Series", series)
    add("Number", issue or "1")
    add("Year", year)
    add("Volume", volume or year or "1")
    add("Publisher", publisher)
    add("Notes", notes or (f"[CVDB:{comicvine_issue_id}]" if comicvine_issue_id else ""))
    add("Web", web)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_metroninfo(series: str, issue: str, year: str, publisher: str, comicvine_issue_id: str, comicvine_series_id: str) -> bytes:
    root = ET.Element("MetronInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or value == "":
            return
        ET.SubElement(root, tag).text = str(value)

    add("Series", series)
    add("Number", issue or "1")
    add("Year", year)
    add("Publisher", publisher)
    add("ComicVineSeriesId", comicvine_series_id)
    add("ComicVineIssueId", comicvine_issue_id)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_zip(cbz: Path, comicinfo_xml: bytes, metroninfo_xml: bytes) -> None:
    tmp = Path(tempfile.mkstemp(suffix=".cbz", dir=cbz.parent)[1])
    try:
        with zipfile.ZipFile(cbz, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            has_comicinfo = False
            has_metroninfo = False
            for item in zin.infolist():
                lower = item.filename.lower()
                if lower == "comicinfo.xml":
                    has_comicinfo = True
                    continue
                if lower == "metroninfo.xml":
                    has_metroninfo = True
                    continue
                zout.writestr(item, zin.read(item.filename))
            if not has_comicinfo:
                zout.writestr("ComicInfo.xml", comicinfo_xml)
            else:
                zout.writestr("ComicInfo.xml", comicinfo_xml)
            if not has_metroninfo:
                zout.writestr("MetronInfo.xml", metroninfo_xml)
            else:
                zout.writestr("MetronInfo.xml", metroninfo_xml)
        tmp.replace(cbz)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    cache_db = Path(args.cache_db).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    conn = sqlite3.connect(cache_db) if cache_db.exists() else None
    if conn is not None:
        conn.row_factory = sqlite3.Row

    rows: list[PrepassRow] = []

    for cbz in sorted(root.rglob("*.cbz")):
        root_meta = read_root_comicinfo(cbz)
        sidecar = read_series_json(cbz)
        series = root_meta.get("series") or sidecar.get("series") or ""
        publisher = root_meta.get("publisher") or sidecar.get("publisher") or ""
        year = root_meta.get("year") or sidecar.get("year") or ""
        issue = parse_issue_guess(cbz, root_meta)
        cache_row, cache_status = query_cache(conn, series, issue, year, publisher)
        if cache_row is None:
            rows.append(
                PrepassRow(
                    cbz_path=str(cbz),
                    series_guess=series,
                    issue_guess=issue,
                    year_guess=year,
                    publisher_guess=publisher,
                    cache_status=cache_status,
                    match_series="",
                    match_issue_id="",
                    match_series_id="",
                    action="manual_review",
                    note="no_strong_local_match",
                )
            )
            continue

        target_publisher = publisher or "Unknown"
        target_series = str(cache_row["series"]).strip()
        target_volume = str(cache_row["volume"]).strip() or year or "1"
        target_dir = root.parent / target_publisher / f"{target_series} ({target_volume})"
        comicvine_issue_id = str(cache_row["comicvine_issue_id"]).strip()
        comicvine_series_id = str(cache_row["comicvine_series_id"]).strip()
        comicinfo_xml = build_comicinfo(
            series=target_series,
            issue=issue,
            year=year,
            publisher=target_publisher,
            volume=target_volume,
            notes=root_meta.get("notes") or (f"[CVDB:{comicvine_issue_id}]" if comicvine_issue_id else ""),
            web=root_meta.get("web") or "",
            comicvine_issue_id=comicvine_issue_id,
        )
        metroninfo_xml = build_metroninfo(
            series=target_series,
            issue=issue,
            year=year,
            publisher=target_publisher,
            comicvine_issue_id=comicvine_issue_id,
            comicvine_series_id=comicvine_series_id,
        )
        action = "normalize_ready"
        note = "local_cache_match"
        if not args.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = target_dir / cbz.name
            if cbz.parent != target_dir:
                if dest.exists():
                    action = "target_exists"
                    note = "destination_exists"
                else:
                    shutil.move(str(cbz), str(dest))
                    cbz = dest
            if action == "normalize_ready":
                rewrite_zip(cbz, comicinfo_xml, metroninfo_xml)

        rows.append(
            PrepassRow(
                cbz_path=str(cbz),
                series_guess=series,
                issue_guess=issue,
                year_guess=year,
                publisher_guess=publisher,
                cache_status=cache_status,
                match_series=target_series,
                match_issue_id=comicvine_issue_id,
                match_series_id=comicvine_series_id,
                action=action,
                note=note,
            )
        )

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cbz_path",
                "series_guess",
                "issue_guess",
                "year_guess",
                "publisher_guess",
                "cache_status",
                "match_series",
                "match_issue_id",
                "match_series_id",
                "action",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    print(f"scan_root={root}")
    print(f"cache_db={cache_db}")
    print(f"report={report_path}")
    print(f"processed={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
