#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


EXPLICIT_PUBLISHER_BY_SERIES = {
    "2000AD prog": "Rebellion",
    "Amazing Spider-Man": "Marvel",
    "Amazing Spider-Man - Spider-Versity": "Marvel",
    "Cyclops": "Marvel",
    "Marc Spector - Moon Knight": "Marvel",
    "Sentry": "Marvel",
    "Star Wars: Galaxy's Edge - Echoes Of The Empire": "Marvel",
    "Wade Wilson: Deadpool": "Marvel",
}

PUBLISHER_ALIASES = {
    "dc": "DC Comics",
    "idw": "IDW Publishing",
}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Normalize loose CBZ intake when publisher/series are known but no CV cache match exists.")
    ap.add_argument("--root", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


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
    issue = (issue or "1").replace("One-Shot", "1")
    return {"series": series, "issue": issue.lstrip("0") or "0", "year": year}


def read_comicinfo(cbz: Path) -> tuple[ET.Element | None, dict[str, str]]:
    try:
        with zipfile.ZipFile(cbz, "r") as zf:
            target = next(
                (n for n in zf.namelist() if n.lower() == "comicinfo.xml" or n.lower().endswith("/comicinfo.xml")),
                None,
            )
            if not target:
                return None, {}
            root = ET.fromstring(zf.read(target))
    except Exception:
        return None, {}
    values: dict[str, str] = {}
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
        values[key] = (el.text or "").strip() if el is not None and el.text else ""
    return root, values


def canonical_publisher(value: str | None, series: str) -> str:
    raw = (value or "").strip()
    if raw:
        return PUBLISHER_ALIASES.get(raw.lower(), raw)
    return EXPLICIT_PUBLISHER_BY_SERIES.get(series, "")


def build_comicinfo(series: str, issue: str, year: str, volume: str, publisher: str, notes: str, web: str) -> bytes:
    root = ET.Element("ComicInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or value == "":
            return
        ET.SubElement(root, tag).text = str(value)

    add("Series", series)
    add("Number", issue or "1")
    add("Volume", volume or "1")
    add("Publisher", publisher)
    add("Year", year)
    add("Notes", notes)
    add("Web", web)
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
    report_rows: list[dict[str, str]] = []

    for cbz in sorted(root.glob("*.cbz")):
        _, existing = read_comicinfo(cbz)
        inferred = parse_filename(cbz.name)
        series = existing.get("series") or inferred["series"]
        issue = existing.get("issue") or inferred["issue"] or "1"
        year = existing.get("year") or inferred["year"]
        volume = existing.get("volume") or year or "1"
        publisher = canonical_publisher(existing.get("publisher"), series)
        if not publisher:
            report_rows.append({
                "path": str(cbz),
                "status": "unknown_publisher",
                "publisher": "",
                "series": series,
                "issue": issue,
                "year": year,
                "volume": volume,
                "target_dir": "",
            })
            continue

        target_dir = root.parent / publisher / f"{series} ({volume})"
        report_rows.append({
            "path": str(cbz),
            "status": "dry_run" if args.dry_run else "normalized",
            "publisher": publisher,
            "series": series,
            "issue": issue,
            "year": year,
            "volume": volume,
            "target_dir": str(target_dir),
        })

        if args.dry_run:
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / cbz.name
        working = cbz
        if cbz.parent != target_dir:
            if dest.exists():
                report_rows[-1]["status"] = "target_exists"
                report_rows[-1]["target_dir"] = str(dest)
                continue
            shutil.move(str(cbz), str(dest))
            working = dest

        xml = build_comicinfo(
            series=series,
            issue=issue,
            year=year,
            volume=volume,
            publisher=publisher,
            notes=existing.get("notes", ""),
            web=existing.get("web", ""),
        )
        replace_root_comicinfo(working, xml)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["path", "status", "publisher", "series", "issue", "year", "volume", "target_dir"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"root={root}")
    print(f"report={report}")
    print(f"processed={len(report_rows)}")
    print(f"normalized={sum(1 for r in report_rows if r['status'] == 'normalized')}")
    unresolved = {}
    for row in report_rows:
        if row["status"] not in {"normalized", "dry_run"}:
            unresolved[row["status"]] = unresolved.get(row["status"], 0) + 1
    for key, value in sorted(unresolved.items()):
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
