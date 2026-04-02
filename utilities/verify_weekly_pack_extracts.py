#!/usr/bin/env python3
"""Verify extracted weekly-pack publisher directories against source zip archives.

Compares each non-WebP zip archive under a weekly pack directory to the
same-named extracted publisher directory. Only `.cbz`, `.cbr`, and `.pdf`
payload files are counted. This utility is intended to validate whether a
weekly-pack tree is trustworthy as a larger test corpus.
"""

from __future__ import annotations

import argparse
import csv
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_ROOTS = [
    Path("/mnt/phoenix/media/incoming/weekly-lots"),
    Path("/mnt/phoenix/media/incoming/reality_weekly-lots"),
]
DEFAULT_REPORT_DIR = Path("/mnt/phoenix/staging/verify_weekly_pack_extracts/reports")
VALID_SUFFIXES = {".cbz", ".cbr", ".pdf"}


@dataclass
class VerifyRow:
    root: str
    pack: str
    zip_name: str
    target_dir: str
    status: str
    zip_count: int
    dir_count: int
    missing_count: int
    extra_count: int
    sample_missing: str
    sample_extra: str


def timestamped_report_path(report_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / f"verify_weekly_pack_extracts_{ts}.csv"


def payload_name_set_from_zip(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as zf:
        return {
            Path(name).name
            for name in zf.namelist()
            if not name.endswith("/")
            and "webp" not in name.casefold()
            and Path(name).suffix.casefold() in VALID_SUFFIXES
        }


def payload_name_set_from_dir(path: Path) -> set[str]:
    return {
        p.name
        for p in path.rglob("*")
        if p.is_file() and "webp" not in p.name.casefold() and p.suffix.casefold() in VALID_SUFFIXES
    }


def should_skip_name(name: str) -> bool:
    return "webp" in name.casefold()


def safe_text(value: str) -> str:
    return value.encode("utf-8", "replace").decode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roots",
        nargs="*",
        default=[str(p) for p in DEFAULT_ROOTS],
        help="Weekly-pack roots to verify",
    )
    parser.add_argument("--report", default="", help="Optional explicit CSV report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roots = [Path(p).resolve() for p in args.roots]
    report_path = Path(args.report).resolve() if args.report else timestamped_report_path(DEFAULT_REPORT_DIR)

    rows: list[VerifyRow] = []
    for root in roots:
        if not root.exists():
            rows.append(
                VerifyRow(
                    root=str(root),
                    pack="",
                    zip_name="",
                    target_dir="",
                    status="missing_root",
                    zip_count=0,
                    dir_count=0,
                    missing_count=0,
                    extra_count=0,
                    sample_missing="",
                    sample_extra="",
                )
            )
            continue

        for pack in sorted([p for p in root.iterdir() if p.is_dir()]):
            dirs = {d.name: d for d in pack.iterdir() if d.is_dir() and not should_skip_name(d.name)}
            zips = sorted([z for z in pack.glob("*.zip") if not should_skip_name(z.name)])
            for z in zips:
                target = dirs.get(z.stem)
                if target is None:
                    rows.append(
                        VerifyRow(
                            root=str(root),
                            pack=pack.name,
                            zip_name=z.name,
                            target_dir="",
                            status="missing_dir",
                            zip_count=0,
                            dir_count=0,
                            missing_count=0,
                            extra_count=0,
                            sample_missing="",
                            sample_extra="",
                        )
                    )
                    continue

                zip_set = payload_name_set_from_zip(z)
                dir_set = payload_name_set_from_dir(target)
                missing = sorted(zip_set - dir_set)
                extra = sorted(dir_set - zip_set)
                status = "ok" if not missing and not extra else "mismatch"
                rows.append(
                    VerifyRow(
                        root=str(root),
                        pack=pack.name,
                        zip_name=z.name,
                        target_dir=target.name,
                        status=status,
                        zip_count=len(zip_set),
                        dir_count=len(dir_set),
                        missing_count=len(missing),
                        extra_count=len(extra),
                        sample_missing=" | ".join(missing[:3]),
                        sample_extra=" | ".join(extra[:3]),
                    )
                )

    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "root",
                "pack",
                "zip_name",
                "target_dir",
                "status",
                "zip_count",
                "dir_count",
                "missing_count",
                "extra_count",
                "sample_missing",
                "sample_extra",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_text(str(value)) for key, value in row.__dict__.items()})

    ok = sum(1 for row in rows if row.status == "ok")
    mismatch = sum(1 for row in rows if row.status == "mismatch")
    missing_dir = sum(1 for row in rows if row.status == "missing_dir")
    print(f"report={report_path}")
    print(f"rows={len(rows)} ok={ok} mismatch={mismatch} missing_dir={missing_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
