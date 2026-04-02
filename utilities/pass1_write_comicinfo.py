#!/usr/bin/env python3
"""Run Pass 1 ComicInfo.xml creation for high-confidence ComicVine matches.

Pipeline:
- scan intake `.cbz` files
- skip anything explicitly labeled `WebP`
- skip archives already Mylar-valid per `cbz_audit.py`
- resolve likely ComicVine issue ids with `cv_issue_resolver.py`
- only act on `resolved` rows
- call ComicTagger with direct `--id` write flow
- re-audit the archive and record whether it is now Mylar-valid

This utility intentionally avoids auto-tagging `candidate` or `unresolved`
resolver results.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cbz_audit import audit_cbz
from cv_issue_resolver import DEFAULT_CONFIG, ResolutionRow, load_cv_config, resolve_issue


DEFAULT_ROOT = Path("/mnt/phoenix/media/incoming")
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/pass1_write_comicinfo/reports")
DEFAULT_COMICTAGGER = Path("/tmp/comictagger-pass1b/bin/comictagger")


@dataclass
class Pass1Row:
    cbz_path: str
    resolver_status: str
    resolver_confidence: str
    resolver_note: str
    issue_id: str
    write_attempted: int
    write_ok: int
    audit_before_valid: int
    audit_after_valid: int
    comicvine_reference_after: str
    note: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"pass1_write_comicinfo_{ts}.csv"


def should_skip_webp(path: Path) -> bool:
    lower = str(path).casefold()
    return "webp" in lower


def load_cv_url(path: Path) -> str:
    cp = configparser.ConfigParser()
    cp.read(path)
    return cp.get("CV", "comicvine_url", fallback="https://comicvine.gamespot.com/api/").strip()


def iter_cbz(root: Path) -> list[Path]:
    return sorted(root.rglob("*.cbz"))


def run_comictagger(
    *,
    comictagger_bin: Path,
    cbz_path: Path,
    issue_id: str,
    api_key: str,
    base_url: str,
    user_agent: str,
    work_root: Path,
    dry_run: bool,
) -> tuple[bool, str]:
    if dry_run:
        return True, "dry_run"

    env = dict(os.environ)
    cache_root = work_root / "cache"
    config_root = work_root / "config"
    cache_root.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)
    env["XDG_CACHE_HOME"] = str(cache_root)
    env["XDG_CONFIG_HOME"] = str(config_root)

    cmd = [
        str(comictagger_bin),
        "--no-gui",
        "-s",
        "-o",
        "--id",
        issue_id,
        "--source",
        "comicvine",
        "--comicvine-key",
        api_key,
        "--comicvine-url",
        base_url,
        "--tags-write",
        "cr",
        str(cbz_path),
    ]
    try:
        proc = subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
            check=False,
        )
    except Exception as exc:
        return False, f"comictagger_exec_failed: {exc}"

    if proc.returncode != 0:
        summary = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "nonzero_exit"
        return False, f"comictagger_failed: {summary}"
    return True, ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan for .cbz files")
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of files to process")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="ComicVine config file")
    parser.add_argument(
        "--comictagger-bin",
        default=str(DEFAULT_COMICTAGGER),
        help="Path to the working ComicTagger CLI binary",
    )
    parser.add_argument(
        "--work-root",
        default="/tmp/cirrus-pass1-write-comicinfo",
        help="Writable root for ComicTagger cache/config scratch space",
    )
    parser.add_argument("--dry-run", action="store_true", help="Resolve and report without writing tags")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)
    comictagger_bin = Path(args.comictagger_bin).resolve()
    work_root = Path(args.work_root).resolve()

    api_key, user_agent, base_url, rate = load_cv_config(Path(args.config))
    rows: list[Pass1Row] = []

    count = 0
    for cbz_path in iter_cbz(root):
        if args.limit and count >= args.limit:
            break
        count += 1

        if should_skip_webp(cbz_path):
            rows.append(
                Pass1Row(
                    cbz_path=str(cbz_path),
                    resolver_status="skipped",
                    resolver_confidence="none",
                    resolver_note="webp_labeled",
                    issue_id="",
                    write_attempted=0,
                    write_ok=0,
                    audit_before_valid=0,
                    audit_after_valid=0,
                    comicvine_reference_after="",
                    note="skipped_webp",
                )
            )
            continue

        before = audit_cbz(cbz_path)
        if before.mylar_import_valid:
            rows.append(
                Pass1Row(
                    cbz_path=str(cbz_path),
                    resolver_status="skipped",
                    resolver_confidence="none",
                    resolver_note="already_mylar_valid",
                    issue_id=before.comicvine_reference_value,
                    write_attempted=0,
                    write_ok=0,
                    audit_before_valid=before.mylar_import_valid,
                    audit_after_valid=before.mylar_import_valid,
                    comicvine_reference_after=before.comicvine_reference_value,
                    note="already_valid",
                )
            )
            continue

        resolved: ResolutionRow = resolve_issue(
            cbz_path,
            api_key=api_key,
            user_agent=user_agent,
            base_url=base_url,
            rate=rate,
        )

        if resolved.status != "resolved" or not resolved.issue_id:
            rows.append(
                Pass1Row(
                    cbz_path=str(cbz_path),
                    resolver_status=resolved.status,
                    resolver_confidence=resolved.confidence,
                    resolver_note=resolved.note,
                    issue_id=resolved.issue_id,
                    write_attempted=0,
                    write_ok=0,
                    audit_before_valid=before.mylar_import_valid,
                    audit_after_valid=before.mylar_import_valid,
                    comicvine_reference_after=before.comicvine_reference_value,
                    note="not_written",
                )
            )
            continue

        ok, note = run_comictagger(
            comictagger_bin=comictagger_bin,
            cbz_path=cbz_path,
            issue_id=resolved.issue_id,
            api_key=api_key,
            base_url=load_cv_url(Path(args.config)),
            user_agent=user_agent,
            work_root=work_root,
            dry_run=args.dry_run,
        )
        after = audit_cbz(cbz_path) if ok else before
        rows.append(
            Pass1Row(
                cbz_path=str(cbz_path),
                resolver_status=resolved.status,
                resolver_confidence=resolved.confidence,
                resolver_note=resolved.note,
                issue_id=resolved.issue_id,
                write_attempted=1,
                write_ok=int(ok),
                audit_before_valid=before.mylar_import_valid,
                audit_after_valid=after.mylar_import_valid,
                comicvine_reference_after=after.comicvine_reference_value,
                note=note,
            )
        )

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cbz_path",
                "resolver_status",
                "resolver_confidence",
                "resolver_note",
                "issue_id",
                "write_attempted",
                "write_ok",
                "audit_before_valid",
                "audit_after_valid",
                "comicvine_reference_after",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    written = sum(1 for row in rows if row.write_attempted)
    write_ok = sum(1 for row in rows if row.write_ok)
    now_valid = sum(1 for row in rows if row.audit_after_valid)
    skipped = sum(1 for row in rows if row.resolver_status == "skipped")
    print(f"scan_root={root}")
    print(f"report={report_path}")
    print(
        f"processed={len(rows)} write_attempted={written} write_ok={write_ok} "
        f"now_valid={now_valid} skipped={skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
