#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Write ISBN/library-oriented ComicInfo.xml and MetronInfo.xml into CBZ files.")
    ap.add_argument("--manifest", required=True, help="JSON manifest describing books to process")
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def add(parent: ET.Element, tag: str, value: str | None) -> None:
    if value is None or value == "":
        return
    ET.SubElement(parent, tag).text = str(value)


def build_comicinfo(book: dict) -> bytes:
    root = ET.Element("ComicInfo")
    add(root, "Title", book.get("title"))
    add(root, "Series", book.get("series"))
    add(root, "Number", book.get("number"))
    add(root, "Count", book.get("count"))
    add(root, "Volume", book.get("volume"))
    add(root, "SeriesGroup", book.get("series_group"))
    add(root, "Summary", book.get("summary"))
    add(root, "Notes", book.get("notes"))
    add(root, "Web", book.get("web"))
    add(root, "Year", book.get("year"))
    add(root, "Month", book.get("month"))
    add(root, "Day", book.get("day"))
    add(root, "Publisher", book.get("publisher"))
    add(root, "Imprint", book.get("imprint"))
    add(root, "PageCount", book.get("page_count"))
    add(root, "Format", book.get("format"))
    add(root, "Genre", book.get("genre"))
    add(root, "Writer", book.get("writer"))
    add(root, "Penciller", book.get("penciller"))
    add(root, "Inker", book.get("inker"))
    add(root, "Colorist", book.get("colorist"))
    add(root, "Letterer", book.get("letterer"))
    add(root, "CoverArtist", book.get("cover_artist"))
    add(root, "ScanInformation", book.get("scan_information"))
    add(root, "Tags", book.get("tags"))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_metroninfo(book: dict) -> bytes:
    root = ET.Element("MetronInfo")
    add(root, "Series", book.get("series"))
    add(root, "Title", book.get("title"))
    add(root, "Number", book.get("number"))
    add(root, "Count", book.get("count"))
    add(root, "Volume", book.get("volume"))
    add(root, "Publisher", book.get("publisher"))

    year = book.get("year")
    month = book.get("month")
    day = book.get("day") or "01"
    if year and month:
        add(root, "CoverDate", f"{year}-{int(month):02d}-{int(day):02d}")

    add(root, "Format", book.get("format"))
    add(root, "Summary", book.get("summary"))
    add(root, "ISBN", book.get("isbn"))
    add(root, "Database", book.get("database"))
    add(root, "DatabaseId", book.get("database_id"))
    add(root, "Source", book.get("source"))
    add(root, "Notes", book.get("notes"))
    add(root, "Web", book.get("web"))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_archive(cbz_path: Path, comicinfo_xml: bytes, metroninfo_xml: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(suffix=".cbz", dir=str(cbz_path.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        with zipfile.ZipFile(cbz_path, "r") as zin, zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                lower_name = item.filename.lower()
                if lower_name in {"comicinfo.xml", "metroninfo.xml", "metroninfo.cml"}:
                    continue
                zout.writestr(item, zin.read(item.filename))
            zout.writestr("ComicInfo.xml", comicinfo_xml)
            zout.writestr("MetronInfo.xml", metroninfo_xml)
        os.replace(tmp_path, cbz_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    books = json.loads(manifest_path.read_text(encoding="utf-8"))
    for book in books:
        try:
            source = Path(book["source_path"])
            dest = Path(book["dest_path"])
            if not source.exists():
                print(f"missing_source {source}")
                continue
            if not args.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if source.resolve() != dest.resolve():
                    if dest.exists():
                        print(f"target_exists {dest}")
                        continue
                    shutil.move(str(source), str(dest))
                rewrite_archive(dest, build_comicinfo(book), build_metroninfo(book))
            print(f"processed {dest}")
        except Exception as exc:
            print(f"error {book.get('dest_path') or book.get('source_path')}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
