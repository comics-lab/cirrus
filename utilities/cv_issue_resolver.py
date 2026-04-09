#!/usr/bin/env python3
"""Resolve ComicVine issue ids for intake CBZ files.

Current default focus:
- scan `/mnt/phoenix/media/incoming/jdownloader`
- inspect `.cbz` files only
- infer series / issue number / year from existing root ComicInfo.xml,
  archive filename, and parent directory name
- search ComicVine for matching volumes and issues
- emit a CSV report with best candidates

This utility does not write tags. It exists to feed the Pass 1 ComicTagger
write path with a deterministic `issue_id` when possible.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming/jdownloader")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/cv_issue_resolver/reports")
DEFAULT_CONFIG = Path("/home/rmleonard/Projects/mylar-library/config.ini")


@dataclass
class Candidate:
    volume_id: str
    volume_name: str
    volume_year: str
    publisher: str
    score: int


@dataclass
class ResolutionRow:
    cbz_path: str
    series_guess: str
    issue_number_guess: str
    year_guess: str
    publisher_guess: str
    volume_id: str
    volume_name: str
    volume_year: str
    issue_id: str
    issue_name: str
    issue_cover_date: str
    candidate_score: str
    confidence: str
    status: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"cv_issue_resolver_{ts}.csv"


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
            if exc.code == 420 and attempt < retries:
                time.sleep(backoff)
                continue
            raise


def split_path(value: str) -> list[str]:
    return [part for part in value.replace("\\", "/").split("/") if part]


def parse_root_comicinfo(path: Path) -> dict[str, str]:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            root_name = None
            for name in zf.namelist():
                parts = split_path(name)
                if len(parts) == 1 and parts[0].lower() == "comicinfo.xml":
                    root_name = name
                    break
            if not root_name:
                return {}
            root = ET.fromstring(zf.read(root_name))
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
        "title": text("Title"),
    }


def normalize_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def strip_release_noise(value: str) -> str:
    value = re.sub(r"\((?:digital|webrip|hybrid)[^)]+\)", "", value, flags=re.I)
    value = re.sub(r"\((?:graphic novel|tpb|hardcover|hard cover)[^)]+\)", "", value, flags=re.I)
    value = re.sub(r"\([^)]*(?:tomjoad|leduch|magicman|empire|digital-hd)[^)]*\)", "", value, flags=re.I)
    value = value.replace("–", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -")


def parse_issue_number(value: str) -> str:
    patterns = [
        r"#\s*([0-9]+[A-Za-z\.\-/]*)",
        r"\bv(?:ol(?:ume)?)?\.?\s*0*([0-9]+[A-Za-z\.\-/]*)\b",
        r"\b(?:issue|iss)\.?\s*#?\s*0*([0-9]+[A-Za-z\.\-/]*)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, value, flags=re.I)
        if match:
            return match.group(1)
    return ""


def parse_year(value: str) -> str:
    match = re.search(r"\b(19|20)\d{2}\b", value)
    return match.group(0) if match else ""


def infer_series_from_parent(parent_name: str) -> str:
    cleaned = strip_release_noise(parent_name)
    issue_split = re.split(r"\s+#?\d+[A-Za-z]?\s+-\s+", cleaned, maxsplit=1)
    if len(issue_split) == 2:
        left = issue_split[0].strip()
        if left:
            return normalize_name(left)
    if " - " in cleaned:
        left = cleaned.split(" - ", 1)[0].strip()
        if left:
            return left
    cleaned = re.sub(r"\((19|20)\d{2}\)", "", cleaned).strip(" -")
    return normalize_name(cleaned)


def infer_title_from_parent(parent_name: str) -> str:
    cleaned = strip_release_noise(parent_name)
    issue_split = re.split(r"\s+#?\d+[A-Za-z]?\s+-\s+", cleaned, maxsplit=1)
    if len(issue_split) == 2:
        return normalize_name(issue_split[1])
    if " - " in cleaned:
        right = cleaned.split(" - ", 1)[1].strip()
        return normalize_name(re.sub(r"\((19|20)\d{2}\)", "", right).strip(" -"))
    return ""


def infer_from_path(path: Path) -> dict[str, str]:
    parent_name = path.parent.name
    stem = strip_release_noise(path.stem)
    number = parse_issue_number(stem) or parse_issue_number(parent_name)
    year = parse_year(parent_name) or parse_year(stem)
    if number and year and number == year:
        number = ""
    return {
        "series": infer_series_from_parent(parent_name),
        "number": number,
        "year": year,
        "title": infer_title_from_parent(parent_name),
        "publisher": "",
    }


def text_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, normalize_name(left).casefold(), normalize_name(right).casefold()).ratio()


def best_volume_match(
    results: list[dict], series_name: str, year: str, publisher: str, title: str
) -> Candidate | None:
    if not results:
        return None
    needle = normalize_name(series_name).casefold()
    pub_needle = normalize_name(publisher).casefold()
    best: Candidate | None = None
    for result in results:
        name = normalize_name(result.get("name") or "")
        start_year = str(result.get("start_year") or "")
        pub = ""
        if result.get("publisher"):
            pub = normalize_name(result["publisher"].get("name") or "")
        score = 0
        if name.casefold() == needle:
            score += 6
        elif needle and needle in name.casefold():
            score += 4
        else:
            similarity = text_similarity(series_name, name)
            if similarity >= 0.9:
                score += 5
            elif similarity >= 0.75:
                score += 3
            elif similarity >= 0.6:
                score += 1
        if title:
            title_similarity = text_similarity(title, name)
            if title_similarity >= 0.9:
                score += 6
            elif title_similarity >= 0.75:
                score += 4
            elif title_similarity >= 0.6:
                score += 2
            title_fold = normalize_name(title).casefold()
            if title_fold and title_fold in name.casefold():
                score += 3
        if year and start_year == year:
            score += 3
        if pub_needle and pub.casefold() == pub_needle:
            score += 2
        candidate = Candidate(
            volume_id=str(result.get("id") or ""),
            volume_name=name,
            volume_year=start_year,
            publisher=pub,
            score=score,
        )
        if best is None or candidate.score > best.score:
            best = candidate
    return best


def best_issue_search_match(results: list[dict], title: str, year: str, publisher: str) -> dict | None:
    title_fold = normalize_name(title).casefold()
    pub_fold = normalize_name(publisher).casefold()
    best = None
    best_score = -1
    for issue in results:
        issue_name = normalize_name(issue.get("name") or "")
        issue_year = str(issue.get("cover_date") or "")[:4]
        volume = issue.get("volume") or {}
        issue_pub = ""
        if issue.get("publisher") and isinstance(issue.get("publisher"), dict):
            issue_pub = normalize_name(issue["publisher"].get("name") or "")
        score = 0
        if title_fold and title_fold == issue_name.casefold():
            score += 8
        elif title and text_similarity(title, issue_name) >= 0.8:
            score += 5
        elif title and text_similarity(title, issue_name) >= 0.6:
            score += 2
        if year and issue_year == year:
            score += 3
        if pub_fold and issue_pub.casefold() == pub_fold:
            score += 2
        if score > best_score:
            best = issue
            best_score = score
    return best


def best_issue_number_match(
    results: list[dict], series: str, number: str, year: str, publisher: str
) -> dict | None:
    series_fold = normalize_name(series).casefold()
    pub_fold = normalize_name(publisher).casefold()
    best = None
    best_score = -1
    for issue in results:
        issue_number = str(issue.get("issue_number") or "").strip()
        issue_year = str(issue.get("cover_date") or "")[:4]
        issue_name = normalize_name(issue.get("name") or "")
        volume = issue.get("volume") or {}
        volume_name = normalize_name(volume.get("name") or "")
        issue_pub = ""
        publisher_block = issue.get("publisher")
        if isinstance(publisher_block, dict):
            issue_pub = normalize_name(publisher_block.get("name") or "")

        score = 0
        if number and issue_number == number:
            score += 8
        elif number:
            continue
        if year:
            if issue_year and issue_year != year:
                continue
            if not issue_year:
                continue
        if volume_name.casefold() == series_fold:
            score += 7
        elif series_fold and series_fold in volume_name.casefold():
            score += 4
        else:
            similarity = text_similarity(series, volume_name)
            if similarity >= 0.9:
                score += 5
            elif similarity >= 0.75:
                score += 3
        if year and issue_year == year:
            score += 3
        if pub_fold and issue_pub.casefold() == pub_fold:
            score += 2
        if issue_name:
            score += 1
        if score > best_score:
            best = issue
            best_score = score
    return best


def resolve_issue(
    path: Path,
    *,
    api_key: str,
    user_agent: str,
    base_url: str,
    rate: float,
) -> ResolutionRow:
    ci = parse_root_comicinfo(path)
    inferred = infer_from_path(path)
    series = ci.get("series") or inferred["series"]
    number = ci.get("number") or inferred["number"]
    year = ci.get("year") or inferred["year"]
    publisher = ci.get("publisher") or inferred["publisher"]
    title = ci.get("title") or inferred["title"]

    if not series:
        return ResolutionRow(
            cbz_path=str(path),
            series_guess=series,
            issue_number_guess=number,
            year_guess=year,
            publisher_guess=publisher,
            volume_id="",
            volume_name="",
            volume_year="",
            issue_id="",
            issue_name="",
            issue_cover_date="",
            candidate_score="",
            confidence="none",
            status="unresolved",
            note="no_series_guess",
        )

    try:
        vol_search = cv_request(
            base_url=base_url,
            api_key=api_key,
            user_agent=user_agent,
            endpoint="search",
            params={"resources": "volume", "query": series, "limit": "20"},
        )
    except Exception as exc:
        return ResolutionRow(
            cbz_path=str(path),
            series_guess=series,
            issue_number_guess=number,
            year_guess=year,
            publisher_guess=publisher,
            volume_id="",
            volume_name="",
            volume_year="",
            issue_id="",
            issue_name="",
            issue_cover_date="",
            candidate_score="",
            confidence="none",
            status="error",
            note=f"volume_search_failed: {exc}",
        )

    volume = best_volume_match(vol_search.get("results", []), series, year, publisher, title)
    if volume is None or not volume.volume_id:
        return ResolutionRow(
            cbz_path=str(path),
            series_guess=series,
            issue_number_guess=number,
            year_guess=year,
            publisher_guess=publisher,
            volume_id="",
            volume_name="",
            volume_year="",
            issue_id="",
            issue_name="",
            issue_cover_date="",
            candidate_score="",
            confidence="none",
            status="unresolved",
            note="no_volume_match",
        )

    issue_id = ""
    issue_name = ""
    issue_cover_date = ""
    note = ""

    if number:
        try:
            issues = cv_request(
                base_url=base_url,
                api_key=api_key,
                user_agent=user_agent,
                endpoint="issues",
                params={"filter": f"volume:{volume.volume_id},issue_number:{number}", "limit": "5"},
            )
        except Exception as exc:
            note = f"issue_lookup_failed: {exc}"
            issues = {}
        results = issues.get("results", []) if issues else []
        if results:
            issue = results[0]
            issue_id = str(issue.get("id") or "")
            issue_name = issue.get("name") or ""
            issue_cover_date = issue.get("cover_date") or ""
        else:
            try:
                issue_search = cv_request(
                    base_url=base_url,
                    api_key=api_key,
                    user_agent=user_agent,
                    endpoint="search",
                    params={"resources": "issue", "query": f"{series} {number}", "limit": "10"},
                )
            except Exception as exc:
                note = note or f"issue_search_failed: {exc}"
                issue_search = {}
            issue_results = issue_search.get("results", []) if issue_search else []
            best_issue = best_issue_number_match(issue_results, series, number, year, publisher)
            if best_issue is not None:
                best_vol = best_issue.get("volume") or {}
                issue_id = str(best_issue.get("id") or "")
                issue_name = best_issue.get("name") or ""
                issue_cover_date = best_issue.get("cover_date") or ""
                volume = Candidate(
                    volume_id=str(best_vol.get("id") or volume.volume_id),
                    volume_name=normalize_name(best_vol.get("name") or volume.volume_name),
                    volume_year=str(best_vol.get("start_year") or (year if year else "")),
                    publisher=volume.publisher,
                    score=max(volume.score, 10),
                )
                note = "issue_number_search_fallback"
            else:
                note = note or "no_issue_match"
    elif title:
        try:
            issues = cv_request(
                base_url=base_url,
                api_key=api_key,
                user_agent=user_agent,
                endpoint="search",
                params={"resources": "issue", "query": f"{series} {title}", "limit": "10"},
            )
        except Exception as exc:
            note = f"issue_search_failed: {exc}"
            issues = {}
        issue_results = issues.get("results", []) if issues else []
        for issue in issue_results:
            issue_vol = issue.get("volume") or {}
            if str(issue_vol.get("id") or "") == volume.volume_id:
                issue_id = str(issue.get("id") or "")
                issue_name = issue.get("name") or ""
                issue_cover_date = issue.get("cover_date") or ""
                break
        if not issue_id:
            best_issue = best_issue_search_match(issue_results, title, year, publisher)
            if best_issue is not None:
                issue_id = str(best_issue.get("id") or "")
                issue_name = best_issue.get("name") or ""
                issue_cover_date = best_issue.get("cover_date") or ""
                note = "issue_search_fallback"
            else:
                note = note or "no_issue_match"
    else:
        note = "no_issue_number_or_title"

    time.sleep(rate)

    confidence = "none"
    status = "unresolved"
    if issue_id:
        if volume.score >= 10 and note not in {"issue_search_fallback"}:
            confidence = "high"
            status = "resolved"
        elif volume.score >= 7:
            confidence = "medium"
            status = "candidate"
            note = note or "needs_review_medium_confidence"
        else:
            confidence = "low"
            status = "candidate"
            note = note or "needs_review_low_confidence"

    return ResolutionRow(
        cbz_path=str(path),
        series_guess=series,
        issue_number_guess=number,
        year_guess=year,
        publisher_guess=publisher,
        volume_id=volume.volume_id,
        volume_name=volume.volume_name,
        volume_year=volume.volume_year,
        issue_id=issue_id,
        issue_name=issue_name,
        issue_cover_date=issue_cover_date,
        candidate_score=str(volume.score),
        confidence=confidence,
        status=status,
        note=note,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan for .cbz files")
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of .cbz files to inspect")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Config file containing ComicVine settings")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key, user_agent, base_url, rate = load_cv_config(Path(args.config))
    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    rows: list[ResolutionRow] = []
    count = 0
    for path in sorted(root.rglob("*.cbz")):
        if args.limit and count >= args.limit:
            break
        rows.append(resolve_issue(path, api_key=api_key, user_agent=user_agent, base_url=base_url, rate=rate))
        count += 1

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cbz_path",
                "series_guess",
                "issue_number_guess",
                "year_guess",
                "publisher_guess",
                "volume_id",
                "volume_name",
                "volume_year",
                "issue_id",
                "issue_name",
                "issue_cover_date",
                "candidate_score",
                "confidence",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    resolved = sum(1 for row in rows if row.status == "resolved")
    candidates = sum(1 for row in rows if row.status == "candidate")
    unresolved = sum(1 for row in rows if row.status == "unresolved")
    errors = sum(1 for row in rows if row.status == "error")
    print(f"scan_root={root}")
    print(f"report={report_path}")
    print(
        f"processed={len(rows)} resolved={resolved} candidates={candidates} "
        f"unresolved={unresolved} errors={errors}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
