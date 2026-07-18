#!/usr/bin/env python3
"""V3 Mylar buildout normalizer for staged intake trees.

This utility is intentionally separate from the existing intake pipeline. It
operates on a buildout tree that is already past archive conversion and tries to
shape it toward the Mylar layout defined in config.ini:

- folder_format = $Publisher/$Series $Type ($Year)
- file_format = $Series $VolumeN $Annual #$Issue ($monthname $Year)

It also preserves provenance by writing the original filename and normalization
timestamp into the generated sidecars and XML metadata.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import re
import shutil
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utilities.mylar_name_normalize import normalize_filename


DEFAULT_SOURCE_ROOT = Path("/mnt/phoenix/media/incoming/mylar-DUMMY-ROOT")
DEFAULT_IMPORT_ROOT = Path("/mnt/phoenix/media/incoming/mylar-imports")
DEFAULT_MYLAR_CONFIG = Path("/mnt/phoenix/services/mylar/mylar/config.ini")
DEFAULT_REPORT_DIR = Path("/home/rmleonard/Projects/cirrus/data/reports")


@dataclass
class SeriesJob:
    source_dir: Path
    target_dir: Path
    publisher: str
    series: str
    year: str
    volume: str
    series_type: str
    comicid: str
    files: list[Path]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    ap.add_argument("--import-root", default=str(DEFAULT_IMPORT_ROOT))
    ap.add_argument("--mylar-config", default=str(DEFAULT_MYLAR_CONFIG))
    ap.add_argument("--report", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--promote", action="store_true", help="Copy normalized branches into the import root")
    ap.add_argument(
        "--move",
        action="store_true",
        help="Move normalized branches into the import root instead of copying them",
    )
    ap.add_argument(
        "--v3-only",
        action="store_true",
        default=True,
        help="Only process paths tagged with v3 in the path or filename",
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Override --v3-only and process every detected CBZ branch",
    )
    return ap.parse_args()


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def read_config(path: Path) -> tuple[str, str]:
    cfg = configparser.ConfigParser()
    if not cfg.read(path):
        return "$Publisher/$Series $Type ($Year)", "$Series $VolumeN $Annual #$Issue ($monthname $Year)"
    folder = cfg.get("StoryArcs", "folder_format", fallback=None)
    file_format = cfg.get("StoryArcs", "file_format", fallback=None)
    folder = folder or cfg.get("Mylar", "folder_format", fallback=None) or "$Publisher/$Series $Type ($Year)"
    file_format = file_format or cfg.get("Mylar", "file_format", fallback=None) or "$Series $VolumeN $Annual #$Issue ($monthname $Year)"
    return folder, file_format


def normalize_component(value: str) -> str:
    value = re.sub(r"[\/\\]+", " ", (value or "").strip())
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def read_xml_from_cbz(cbz: Path, target_name: str) -> ET.Element | None:
    try:
        with zipfile.ZipFile(cbz, "r") as zf:
            target = next(
                (name for name in zf.namelist() if name.lower() == target_name.lower()),
                None,
            )
            if not target:
                return None
            return ET.fromstring(zf.read(target))
    except Exception:
        return None


def read_text_fields(root: ET.Element | None) -> dict[str, str]:
    data: dict[str, str] = {}
    if root is None:
        return data
    for tag in [
        "Series",
        "Number",
        "Year",
        "Month",
        "Day",
        "Publisher",
        "Volume",
        "Type",
        "Notes",
        "Web",
    ]:
        node = root.find(tag)
        data[tag.lower()] = (node.text or "").strip() if node is not None and node.text else ""
    return data


def read_series_json(series_dir: Path) -> dict[str, str]:
    candidate = series_dir / "series.json"
    if not candidate.exists():
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    meta = payload.get("metadata") or {}
    if isinstance(meta, list):
        meta = meta[0] if meta else {}
    if not isinstance(meta, dict):
        return {}
    cirrus = payload.get("cirrus") if isinstance(payload.get("cirrus"), dict) else {}
    out = {
        "series": str(meta.get("name") or meta.get("series") or "").strip(),
        "publisher": str(meta.get("publisher") or "").strip(),
        "year": str(meta.get("year") or "").strip(),
        "comicid": str(meta.get("comicid") or "").strip(),
        "volume": str(meta.get("volume") or meta.get("start_year") or "").strip(),
        "type": str(meta.get("booktype") or "").strip(),
    }
    if cirrus:
        out["original_filename"] = str(cirrus.get("original_filename") or "").strip()
    return out


def parse_filename(path: Path) -> dict[str, str]:
    stem = path.stem
    year_match = re.search(r"\((19|20)\d{2}\)", stem)
    year = year_match.group(0).strip("()") if year_match else ""
    base = re.sub(r"\s*\([^)]*\)\s*$", "", stem)
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
    return {
        "series": series.strip(),
        "issue": (issue or "1").replace("One-Shot", "1").lstrip("0") or "0",
        "year": year,
    }


def find_branch_dirs(root: Path, v3_only: bool) -> list[Path]:
    series_dirs = sorted({cbz.parent for cbz in root.rglob("*.cbz")})
    if not v3_only:
        return series_dirs
    return [p for p in series_dirs if "v3" in str(p).lower() or any("v3" in part.lower() for part in p.parts)]


def find_comicid(values: dict[str, str]) -> str:
    for key in ("comicid", "web", "notes"):
        value = values.get(key, "")
        if not value:
            continue
        m = re.search(r"(?:4050-|CVDB:?|CVSERIES)?(\d{3,})", value, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def infer_monthname(values: dict[str, str]) -> str:
    month = values.get("month", "")
    if not month:
        return ""
    try:
        idx = int(month)
    except Exception:
        return month
    if 1 <= idx <= 12:
        return datetime(2000, idx, 1).strftime("%B")
    return ""


def render_file_name(series: str, volume: str, issue: str, year: str, monthname: str, annual: str) -> str:
    volume_token = volume.strip()
    if not volume_token:
        volume_token = "v01"
    elif volume_token.isdigit():
        volume_token = f"v{int(volume_token):02d}"
    elif not volume_token.lower().startswith("v"):
        volume_token = f"v{volume_token}"
    parts = [
        normalize_component(series),
        volume_token,
        annual.strip(),
        f"#{issue or '1'}",
        f"({normalize_component(monthname)} {year})".strip(),
    ]
    return " ".join(part for part in parts if part).replace("  ", " ").strip() + ".cbz"


def render_folder_name(series: str, publisher: str, year: str, series_type: str) -> Path:
    folder = normalize_component(series)
    if series_type:
        folder = f"{folder} {normalize_component(series_type)}"
    if year:
        folder = f"{folder} ({year})"
    return Path(normalize_component(publisher) or "Unknown") / folder


def build_comicinfo(fields: dict[str, str], original_name: str) -> bytes:
    root = ET.Element("ComicInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or str(value).strip() == "":
            return
        ET.SubElement(root, tag).text = str(value).strip()

    add("Series", fields.get("series"))
    add("Number", fields.get("issue") or "1")
    add("Year", fields.get("year"))
    add("Month", fields.get("month"))
    add("Day", fields.get("day"))
    add("Volume", fields.get("volume") or "v01")
    add("Publisher", fields.get("publisher"))
    add("Notes", f"{fields.get('notes', '')} [original:{original_name}] [normalized:{timestamp()}]".strip())
    add("Web", fields.get("web"))
    add("SeriesGroup", fields.get("series_group"))
    add("Title", fields.get("title"))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_metroninfo(fields: dict[str, str], original_name: str) -> bytes:
    root = ET.Element("MetronInfo")

    def add(tag: str, value: str | None) -> None:
        if value is None or str(value).strip() == "":
            return
        ET.SubElement(root, tag).text = str(value).strip()

    add("Series", fields.get("series"))
    add("Number", fields.get("issue") or "1")
    add("Year", fields.get("year"))
    add("Volume", fields.get("volume") or "v01")
    add("Publisher", fields.get("publisher"))
    add("ComicVineSeriesId", fields.get("comicvine_series_id"))
    add("ComicVineIssueId", fields.get("comicvine_issue_id"))
    add("OriginalFilename", original_name)
    add("NormalizedAt", timestamp())
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_cbz(cbz: Path, comicinfo_xml: bytes, metroninfo_xml: bytes) -> None:
    tmp = Path(tempfile.mkstemp(suffix=".cbz", dir=cbz.parent)[1])
    try:
        with zipfile.ZipFile(cbz, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                lower = item.filename.lower()
                if lower == "comicinfo.xml" or lower == "metroninfo.xml":
                    continue
                zout.writestr(item, zin.read(item.filename))
            zout.writestr("ComicInfo.xml", comicinfo_xml)
            zout.writestr("MetronInfo.xml", metroninfo_xml)
        tmp.replace(cbz)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def write_series_json(series_dir: Path, fields: dict[str, str], original_name: str, original_path: Path, dry_run: bool) -> None:
    series_json_path = series_dir / "series.json"
    payload = {}
    if series_json_path.exists():
        try:
            payload = json.loads(series_json_path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            payload = {}
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    metadata.update(
        {
            "name": fields.get("series", metadata.get("name", "")),
            "publisher": fields.get("publisher", metadata.get("publisher", "")),
            "year": fields.get("year", metadata.get("year", "")),
            "comicid": fields.get("comicid", metadata.get("comicid", "")),
        }
    )
    payload["metadata"] = metadata
    cirrus = payload.get("cirrus") if isinstance(payload.get("cirrus"), dict) else {}
    cirrus.update(
        {
            "original_filename": original_name,
            "original_path": str(original_path),
            "normalized_at": timestamp(),
        }
    )
    payload["cirrus"] = cirrus
    if not dry_run:
        series_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_cvinfo(series_dir: Path, comicid: str, series: str, dry_run: bool) -> None:
    if not comicid:
        return
    cvinfo_path = series_dir / "cvinfo"
    if cvinfo_path.exists():
        return
    slug = normalize_component(series).lower().replace(" ", "-")
    url = f"https://comicvine.gamespot.com/{slug}/4050-{comicid}/\n"
    if not dry_run:
        cvinfo_path.write_text(url, encoding="utf-8")


def ensure_target_dir(base: Path, target: Path, dry_run: bool) -> None:
    if dry_run:
        return
    target.mkdir(parents=True, exist_ok=True)


def promote_branch(series_dir: Path, import_root: Path, target_series_dir: Path, dry_run: bool, move: bool) -> None:
    if series_dir.resolve() == target_series_dir.resolve():
        return
    if dry_run:
        return
    target_series_dir.parent.mkdir(parents=True, exist_ok=True)
    if move:
        if target_series_dir.exists():
            for item in series_dir.iterdir():
                dest = target_series_dir / item.name
                if dest.exists():
                    continue
                shutil.move(str(item), str(dest))
            try:
                series_dir.rmdir()
            except OSError:
                pass
        else:
            shutil.move(str(series_dir), str(target_series_dir))
    else:
        if not target_series_dir.exists():
            target_series_dir.mkdir(parents=True, exist_ok=True)
        for item in series_dir.iterdir():
            dest = target_series_dir / item.name
            if item.is_dir():
                if not dest.exists():
                    shutil.copytree(item, dest)
                continue
            if dest.exists():
                continue
            shutil.copy2(item, dest)


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).resolve()
    import_root = Path(args.import_root).resolve()
    config_folder_format, config_file_format = read_config(Path(args.mylar_config).resolve())
    report_path = Path(args.report).resolve() if args.report else DEFAULT_REPORT_DIR / f"mylar_v3_buildout_{timestamp()}.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    series_dirs = find_branch_dirs(source_root, args.v3_only and not args.all)
    rows: list[dict[str, str]] = []

    for series_dir in series_dirs:
        cbzs = sorted(series_dir.glob("*.cbz"))
        if not cbzs:
            continue

        root_xml = read_xml_from_cbz(cbzs[0], "ComicInfo.xml")
        metron_xml = read_xml_from_cbz(cbzs[0], "MetronInfo.xml")
        root_meta = read_text_fields(root_xml)
        metron_meta = read_text_fields(metron_xml)
        sidecar = read_series_json(series_dir)
        inferred = parse_filename(cbzs[0])

        series = normalize_component(root_meta.get("series") or sidecar.get("series") or inferred["series"])
        publisher = normalize_component(root_meta.get("publisher") or sidecar.get("publisher") or "")
        year = (root_meta.get("year") or sidecar.get("year") or inferred["year"] or metron_meta.get("year") or "").strip()
        issue = root_meta.get("number") or inferred["issue"] or "1"
        volume = root_meta.get("volume") or sidecar.get("volume") or year or "v01"
        series_type = root_meta.get("type") or sidecar.get("type") or ("Annual" if "annual" in series_dir.name.lower() else "")
        comicid = sidecar.get("comicid") or find_comicid(root_meta) or find_comicid(metron_meta) or ""

        target_dir = import_root / render_folder_name(series, publisher or "Unknown", year, series_type)
        original_name = cbzs[0].name
        file_name = render_file_name(
            series=series,
            volume=volume,
            issue=issue,
            year=year,
            monthname=infer_monthname(root_meta),
            annual=series_type,
        )

        rows.append(
            {
                "source_dir": str(series_dir),
                "target_dir": str(target_dir),
                "series": series,
                "publisher": publisher,
                "year": year,
                "volume": volume,
                "series_type": series_type,
                "comicid": comicid,
                "status": "dry_run" if args.dry_run else "ready",
                "file_format": config_file_format,
                "folder_format": config_folder_format,
            }
        )

        if args.dry_run:
            continue

        ensure_target_dir(import_root, target_dir, args.dry_run)
        write_series_json(series_dir, {
            "series": series,
            "publisher": publisher or "Unknown",
            "year": year,
            "comicid": comicid,
        }, original_name, cbzs[0], args.dry_run)
        write_cvinfo(series_dir, comicid, series, args.dry_run)

        for cbz in cbzs:
            stem_meta = read_text_fields(read_xml_from_cbz(cbz, "ComicInfo.xml"))
            issue_number = stem_meta.get("number") or parse_filename(cbz)["issue"] or "1"
            file_target = target_dir / render_file_name(
                series=series,
                volume=volume,
                issue=issue_number,
                year=year,
                monthname=infer_monthname(stem_meta),
                annual=series_type,
            )
            if file_target.exists():
                rows[-1]["status"] = "target_exists"
                rows[-1]["detail"] = str(file_target)
                continue
            comicinfo_xml = build_comicinfo(
                {
                    "series": series,
                    "issue": issue_number,
                    "year": year,
                    "month": stem_meta.get("month", ""),
                    "day": stem_meta.get("day", ""),
                    "volume": volume,
                    "publisher": publisher or "Unknown",
                    "notes": stem_meta.get("notes", ""),
                    "web": stem_meta.get("web", ""),
                    "series_group": series_dir.name,
                    "title": stem_meta.get("title", ""),
                    "comicvine_series_id": comicid,
                },
                original_name=cbz.name,
            )
            metroninfo_xml = build_metroninfo(
                {
                    "series": series,
                    "issue": issue_number,
                    "year": year,
                    "volume": volume,
                    "publisher": publisher or "Unknown",
                    "comicvine_series_id": comicid,
                    "comicvine_issue_id": "",
                },
                original_name=cbz.name,
            )
            tmp_target = series_dir / file_target.name
            if cbz != tmp_target:
                cbz.rename(tmp_target)
            rewrite_cbz(tmp_target, comicinfo_xml, metroninfo_xml)

        if args.promote:
            promote_branch(series_dir, import_root, target_dir, args.dry_run, args.move)

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "source_dir",
                "target_dir",
                "series",
                "publisher",
                "year",
                "volume",
                "series_type",
                "comicid",
                "status",
                "detail",
                "folder_format",
                "file_format",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"source_root={source_root}")
    print(f"import_root={import_root}")
    print(f"report={report_path}")
    print(f"processed={len(rows)}")
    print(f"promote={'1' if args.promote else '0'}")
    print(f"move={'1' if args.move else '0'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
