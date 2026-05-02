#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_CACHE_DB = "/home/rmleonard/Projects/cirrus/data/series_cache.sqlite3"

PUBLISHER_ALIASES = {
    "dc": "DC Comics",
    "dc comics": "DC Comics",
    "idw": "IDW Publishing",
    "idw publishing": "IDW Publishing",
    "marvel": "Marvel",
}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Seed loose CBZ files from the local series cache.")
    ap.add_argument("--root", required=True, help="Directory containing loose CBZ files")
    ap.add_argument("--cache-db", default=DEFAULT_CACHE_DB)
    ap.add_argument("--report", required=True)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def normalize_text(value: str | None) -> str:
    s = (value or "").strip().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def canonical_publisher(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    return PUBLISHER_ALIASES.get(normalize_text(raw), raw)


def build_cvinfo(comicid: int, name: str) -> str:
    slug = normalize_text(name).replace(" ", "-")
    return f"https://comicvine.gamespot.com/{slug}/4050-{comicid}/\n"


def parse_filename(name: str) -> dict[str, str]:
    stem = Path(name).stem
    year_match = re.search(r"\((19|20)\d{2}\)", stem)
    year = year_match.group(0).strip("()") if year_match else ""
    base = re.sub(r"\s*\([^)]*\)\s*$", "", stem)
    base = re.sub(r"\s*\([^)]*\)\s*$", "", base)
    issue = ""
    series = base.strip()
    patterns = [
        r"^(.*?)[\s\-:]+(\d{1,4}[A-Za-z]?)$",
        r"^(.*?)[\s\-:]+(\d{1,4}[A-Za-z]?)\s+\(",
        r"^(.*?)[\s\-:]+(One-Shot)$",
    ]
    for pattern in patterns:
        m = re.match(pattern, base, re.IGNORECASE)
        if m:
            series = m.group(1).strip()
            issue = m.group(2).strip()
            break
    if not issue:
        m = re.search(r"(?:^|[\s\-:])(\d{1,4}[A-Za-z]?)(?:$|[\s\(])", base)
        if m:
            issue = m.group(1).strip()
            series = base[: m.start(1)].strip(" -:")
    issue = issue or "1"
    issue = issue.replace("One-Shot", "1")
    return {
        "series": series,
        "issue": issue.lstrip("0") or "0",
        "year": year,
    }


def read_root_comicinfo(cbz: Path) -> ET.Element | None:
    try:
        with zipfile.ZipFile(cbz, "r") as zf:
            target = next(
                (n for n in zf.namelist() if n.lower() == "comicinfo.xml" or n.lower().endswith("/comicinfo.xml")),
                None,
            )
            if not target:
                return None
            return ET.fromstring(zf.read(target))
    except Exception:
        return None


def extract_existing_fields(root: ET.Element | None) -> dict[str, str]:
    fields: dict[str, str] = {}
    if root is None:
        return fields
    for tag, key in [
        ("Series", "series"),
        ("Number", "issue"),
        ("Year", "year"),
        ("Publisher", "publisher"),
        ("Volume", "volume"),
        ("Notes", "notes"),
        ("Web", "web"),
    ]:
        el = root.find(tag)
        fields[key] = (el.text or "").strip() if el is not None and el.text else ""
    return fields


def choose_candidate(rows: list[sqlite3.Row], publisher: str, issue_year: str) -> tuple[sqlite3.Row | None, str]:
    if not rows:
        return None, "no_cache_match"

    pub = canonical_publisher(publisher)
    filtered = rows
    if pub:
        pub_norm = normalize_text(pub)
        pub_rows = [row for row in rows if normalize_text(row["publisher"]) == pub_norm]
        if pub_rows:
            filtered = pub_rows

    by_volume: dict[int, sqlite3.Row] = {}
    for row in filtered:
        by_volume[int(row["comicvine_volume_id"])] = row
    filtered = list(by_volume.values())

    if len(filtered) == 1:
        return filtered[0], "unique_series"

    try:
        year = int(issue_year)
    except Exception:
        year = 0

    if year:
        currentish = [row for row in filtered if row["start_year"] and year - 3 <= int(row["start_year"]) <= year]
        if len(currentish) == 1:
            return currentish[0], "year_window_match"
        if currentish:
            latest = sorted(currentish, key=lambda row: int(row["start_year"]), reverse=True)
            if len(latest) >= 2 and int(latest[0]["start_year"]) != int(latest[1]["start_year"]):
                return latest[0], "latest_year_match"

    return None, "ambiguous_series"


def build_series_json(row: sqlite3.Row) -> str:
    payload = {
        "metadata": {
            "name": row["series_name"],
            "publisher": row["publisher"],
            "year": row["start_year"],
            "comicid": row["comicvine_volume_id"],
            "total_issues": row["issue_count"],
            "publication_run": row["publication_run"],
            "imprint": row["imprint"],
            "booktype": row["booktype"],
            "age_rating": row["age_rating"],
        }
    }
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def build_comicinfo(row: sqlite3.Row, issue: str, year: str, existing: dict[str, str]) -> bytes:
    root = ET.Element("ComicInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or value == "":
            return
        ET.SubElement(root, tag).text = str(value)

    add("Series", row["series_name"])
    add("Number", issue or existing.get("issue") or "1")
    add("Volume", row["start_year"])
    add("Publisher", row["publisher"])
    add("Year", year or existing.get("year"))
    add("Notes", f"[CVSERIES{row['comicvine_volume_id']}]")
    add("Web", (row["cvinfo"] or build_cvinfo(int(row["comicvine_volume_id"]), row["series_name"])).strip())
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def replace_root_comicinfo(cbz: Path, xml: bytes) -> None:
    tmp = Path(tempfile.mkstemp(suffix=".cbz", dir=cbz.parent)[1])
    try:
        with zipfile.ZipFile(cbz, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename.lower() == "comicinfo.xml":
                    continue
                zout.writestr(item, zin.read(item.filename))
            zout.writestr("ComicInfo.xml", xml)
        tmp.replace(cbz)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    con = sqlite3.connect(args.cache_db)
    con.row_factory = sqlite3.Row
    report_rows: list[dict[str, str]] = []

    try:
        for cbz in sorted(root.glob("*.cbz")):
            existing_root = read_root_comicinfo(cbz)
            existing = extract_existing_fields(existing_root)
            inferred = parse_filename(cbz.name)
            series = existing.get("series") or inferred["series"]
            issue = existing.get("issue") or inferred["issue"]
            year = existing.get("year") or inferred["year"]
            publisher = canonical_publisher(existing.get("publisher"))

            rows = con.execute(
                "SELECT * FROM series_cache WHERE series_name_norm=? ORDER BY start_year DESC, comicvine_volume_id DESC",
                (normalize_text(series),),
            ).fetchall()
            chosen, reason = choose_candidate(rows, publisher, year)
            if chosen is None:
                report_rows.append(
                    {
                        "path": str(cbz),
                        "status": reason,
                        "publisher": publisher,
                        "series": series,
                        "issue": issue,
                        "year": year,
                        "target_dir": "",
                    }
                )
                continue

            target_dir = root.parent / chosen["publisher"] / f"{chosen['series_name']} ({chosen['start_year']})"
            report_rows.append(
                {
                    "path": str(cbz),
                    "status": "dry_run" if args.dry_run else "seeded",
                    "publisher": chosen["publisher"],
                    "series": chosen["series_name"],
                    "issue": issue,
                    "year": year,
                    "target_dir": str(target_dir),
                }
            )
            if args.dry_run:
                continue

            target_dir.mkdir(parents=True, exist_ok=True)
            series_json = target_dir / "series.json"
            cvinfo = target_dir / "cvinfo"
            if not series_json.exists():
                series_json.write_text(build_series_json(chosen), encoding="utf-8")
            if not cvinfo.exists():
                cvinfo.write_text((chosen["cvinfo"] or build_cvinfo(int(chosen["comicvine_volume_id"]), chosen["series_name"])), encoding="utf-8")

            working_path = cbz
            if cbz.parent != target_dir:
                dest = target_dir / cbz.name
                if dest.exists():
                    report_rows[-1]["status"] = "target_exists"
                    report_rows[-1]["target_dir"] = str(dest)
                    continue
                shutil.move(str(cbz), str(dest))
                working_path = dest

            xml = build_comicinfo(chosen, issue, year, existing)
            replace_root_comicinfo(working_path, xml)
    finally:
        con.close()

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["path", "status", "publisher", "series", "issue", "year", "target_dir"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"root={root}")
    print(f"report={report}")
    print(f"processed={len(report_rows)}")
    print(f"seeded={sum(1 for r in report_rows if r['status'] == 'seeded')}")
    print(f"dry_run={sum(1 for r in report_rows if r['status'] == 'dry_run')}")
    unresolved = {}
    for row in report_rows:
        if row["status"] not in {"seeded", "dry_run"}:
            unresolved[row["status"]] = unresolved.get(row["status"], 0) + 1
    for key, value in sorted(unresolved.items()):
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
