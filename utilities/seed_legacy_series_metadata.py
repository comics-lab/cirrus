#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_GCD_DB = "/home/rmleonard/Projects/mylar-library/utilities/2025-10-15.db"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping-csv", required=True)
    ap.add_argument("--gcd-db", default=DEFAULT_GCD_DB)
    ap.add_argument("--report", required=True)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def read_mapping_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_series_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    meta = data.get("metadata")
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, list) and meta:
        return meta[0]
    return None


def normalize_name(s: str) -> str:
    s = (s or "").lower().strip()
    s = s.replace("&", "and").replace("/", " ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def gcd_lookup_series(con: sqlite3.Connection, name: str, year: int | None, publisher: str | None) -> tuple | None:
    cur = con.cursor()
    clauses = ["lower(name)=?"]
    params: list[object] = [name.lower()]
    if year:
        clauses.append("year_began=?")
        params.append(year)
    q = f"SELECT id, name, year_began, publisher_id FROM gcd_series WHERE {' AND '.join(clauses)} LIMIT 1"
    row = cur.execute(q, params).fetchone()
    if row:
        return row

    rows = cur.execute(
        "SELECT id, name, year_began, publisher_id FROM gcd_series WHERE year_began=? AND lower(name) LIKE ?",
        (year or 0, f"%{name.lower()}%"),
    ).fetchall() if year else []
    if not rows:
        rows = cur.execute(
            "SELECT id, name, year_began, publisher_id FROM gcd_series WHERE lower(name) LIKE ?",
            (f"%{name.lower()}%",),
        ).fetchall()
    if not rows:
        return None

    pub_norm = normalize_name(publisher or "")
    exact_name = [r for r in rows if normalize_name(r[1]) == normalize_name(name)]
    rows = exact_name or rows
    if pub_norm:
        pub_filtered = []
        for r in rows:
            p = gcd_lookup_publisher(con, r[3]) or ""
            if normalize_name(p) == pub_norm:
                pub_filtered.append(r)
        rows = pub_filtered or rows
    return rows[0]


def gcd_lookup_publisher(con: sqlite3.Connection, pub_id: int | None) -> str | None:
    if not pub_id:
        return None
    cur = con.cursor()
    row = cur.execute("SELECT name FROM gcd_publisher WHERE id=? LIMIT 1", (pub_id,)).fetchone()
    return row[0] if row else None


def gcd_lookup_issue(con: sqlite3.Connection, series_id: int, number: str) -> tuple | None:
    cur = con.cursor()
    row = cur.execute(
        "SELECT number, publication_date, key_date FROM gcd_issue WHERE series_id=? AND number=? LIMIT 1",
        (series_id, number),
    ).fetchone()
    if row:
        return row
    return cur.execute(
        "SELECT number, publication_date, key_date FROM gcd_issue WHERE series_id=? AND number LIKE ? LIMIT 1",
        (series_id, f"{number}%"),
    ).fetchone()


def build_cvinfo(comicid: int, name: str) -> str:
    slug = normalize_name(name).replace(" ", "-")
    return f"https://comicvine.gamespot.com/{slug}/4050-{comicid}/\n"


def parse_issue_number(name: str) -> str | None:
    for pattern in (
        r"#\s*([0-9]+[A-Za-z]?)",
        r"\b(?:v\d+\s+)?([0-9]{1,4}[A-Za-z]?)\b",
    ):
        m = re.search(pattern, name, re.IGNORECASE)
        if m:
            return m.group(1).lstrip("0") or "0"
    return None


def parse_year(name: str) -> str | None:
    m = re.search(r"\((19|20)\d{2}\)", name)
    if m:
        return m.group(0).strip("()")
    return None


def build_comicinfo(meta: dict, issue_number: str | None, issue_date: str | None) -> bytes:
    root = ET.Element("ComicInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or value == "":
            return
        ET.SubElement(root, tag).text = str(value)

    add("Series", meta.get("name"))
    add("Number", issue_number)
    add("Publisher", meta.get("publisher"))
    add("Year", issue_date[0:4] if issue_date and len(issue_date) >= 4 else meta.get("year"))
    if issue_date and len(issue_date) >= 7:
        add("Month", issue_date[5:7])
    add("Notes", f"[CVSERIES{meta.get('comicid')}]")
    comicid = meta.get("comicid")
    if comicid:
        add("Web", build_cvinfo(comicid, meta.get("name") or "").strip())
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def has_root_comicinfo(cbz: Path) -> bool:
    with zipfile.ZipFile(cbz, "r") as zf:
        return any("/" not in n and n.lower() == "comicinfo.xml" for n in zf.namelist())


def insert_comicinfo(cbz: Path, xml: bytes) -> None:
    tmp = Path(tempfile.mkstemp(suffix=".cbz", dir=cbz.parent)[1])
    with zipfile.ZipFile(cbz, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.lower() == "comicinfo.xml":
                continue
            zout.writestr(item, zin.read(item.filename))
        zout.writestr("ComicInfo.xml", xml)
    tmp.replace(cbz)


def main() -> int:
    args = parse_args()
    mappings = read_mapping_csv(Path(args.mapping_csv))
    report_rows: list[dict[str, str]] = []
    con = sqlite3.connect(args.gcd_db)

    for row in mappings:
        target = Path(row["target_dir"])
        source = Path(row["legacy_series_dir"])
        meta = load_series_json(source / "series.json")
        if not meta:
            report_rows.append({"target_dir": str(target), "status": "missing_series_json", "detail": str(source)})
            continue

        series_json_target = target / "series.json"
        cvinfo_target = target / "cvinfo"
        if not args.dry_run:
            if not series_json_target.exists():
                shutil.copy2(source / "series.json", series_json_target)
            if (source / "cvinfo").exists():
                if not cvinfo_target.exists():
                    shutil.copy2(source / "cvinfo", cvinfo_target)
            elif meta.get("comicid") and not cvinfo_target.exists():
                cvinfo_target.write_text(build_cvinfo(meta["comicid"], meta.get("name") or ""), encoding="utf-8")

        series_match = gcd_lookup_series(
            con,
            meta.get("name") or "",
            int(meta["year"]) if meta.get("year") else None,
            meta.get("publisher"),
        )
        series_id = series_match[0] if series_match else None

        cbz_count = 0
        seeded = 0
        for cbz in sorted(target.rglob("*.cbz")):
            cbz_count += 1
            if has_root_comicinfo(cbz):
                continue
            issue_number = parse_issue_number(cbz.stem)
            issue_date = None
            if series_id and issue_number:
                issue = gcd_lookup_issue(con, series_id, issue_number)
                if issue:
                    issue_date = issue[1] or issue[2]
            if issue_date is None:
                year = parse_year(cbz.stem)
                issue_date = f"{year}-01-01" if year else None
            xml = build_comicinfo(meta, issue_number, issue_date)
            if not args.dry_run:
                insert_comicinfo(cbz, xml)
            seeded += 1

        report_rows.append(
            {
                "target_dir": str(target),
                "status": "seeded" if not args.dry_run else "dry_run",
                "detail": f"cbz={cbz_count}; seeded={seeded}; gcd_series_id={series_id or ''}; comicid={meta.get('comicid') or ''}",
            }
        )

    con.close()
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["target_dir", "status", "detail"])
        writer.writeheader()
        writer.writerows(report_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
