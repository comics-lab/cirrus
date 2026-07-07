#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/mnt/phoenix/media/incoming/jdownloader}"
MODE="${2:-dry-run}"
WORKERS="${3:-8}"
REPO_ROOT="/home/rmleonard/Projects/cirrus"
REPORT_PATH="${REPORT_PATH:-}"

cd "$REPO_ROOT"

python3 - "$ROOT" "$MODE" "$WORKERS" <<'PY'
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

root = Path(sys.argv[1]).resolve()
mode = sys.argv[2].lower()
apply_changes = mode in {"apply", "--apply", "commit", "run"}
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
report_arg = Path(__import__("os").environ["REPORT_PATH"]).expanduser().resolve() if __import__("os").environ.get("REPORT_PATH") else None
start_epoch = time.time()
start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(start_epoch))

from utilities.mylar_name_normalize import clean_name, clean_title, normalize_filename

report_dir = Path("/home/rmleonard/Projects/cirrus/data/reports")
archive_dir = root.parent / "archive"
duplicate_dir = root.parent / "mylar-duplicates"
quarantine_dir = root.parent / "mylar-quarantine"
error_dir = root.parent / "mylar-errors"
archive_meta_dir = archive_dir / "_provenance"

comic_exts = {".cbz", ".cbr"}
ignored_dir_names = {".git", "__pycache__"}


@dataclass
class DirAction:
    path: Path
    kind: str
    detail: str


@dataclass
class FileAction:
    src: Path
    dst: Path
    reason: str
    detail: str


def file_sig(path: Path) -> tuple[int, str]:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return path.stat().st_size, h.hexdigest()


def walk_files():
    for p in sorted(root.rglob("*")):
        if p.is_file():
            yield p


def comic_files():
    for p in walk_files():
        if p.suffix.lower() in comic_exts:
            yield p


def inspect_comic(path: Path) -> FileAction | None:
    try:
        if path.stat().st_size == 0:
            return FileAction(
                path,
                quarantine_dir / "zero_length" / path.name,
                "zero_length",
                "empty archive",
            )
        if path.suffix.lower() == ".cbz":
            import zipfile

            with zipfile.ZipFile(path, "r") as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise ValueError(f"zip member failed integrity check: {bad}")
    except Exception as exc:
        return FileAction(
            path,
            quarantine_dir / "corrupt_archive" / path.name,
            "corrupt_archive",
            str(exc),
        )

    key = normalize_filename(clean_name(clean_title(path.name)))
    if key in existing_names and existing_names[key] != path:
        return FileAction(
            path,
            duplicate_dir / "normalized_name" / path.name,
            "duplicate_name",
            f"normalized match to {existing_names[key]}",
        )

    try:
        sig = file_sig(path)
        if sig in existing_sigs and existing_sigs[sig] != path:
            return FileAction(
                path,
                duplicate_dir / "content_hash" / path.name,
                "duplicate_content",
                f"content match to {existing_sigs[sig]}",
            )
    except Exception as exc:
        return FileAction(
            path,
            quarantine_dir / "corrupt_archive" / path.name,
            "corrupt_archive",
            str(exc),
        )

    return None


def action_from_report_item(item: dict) -> DirAction | FileAction:
    if "reason" in item:
        return FileAction(
            Path(item["src"]),
            Path(item["dst"]),
            item["reason"],
            item.get("detail", ""),
        )
    return DirAction(
        Path(item["path"]),
        item["kind"],
        item.get("detail", ""),
    )


def load_report(path: Path) -> tuple[list[DirAction], list[FileAction], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    dirs = [action_from_report_item(item) for item in data.get("directory_actions", [])]
    files = [action_from_report_item(item) for item in data.get("file_actions", [])]
    return dirs, files, data


if apply_changes and report_arg:
    report_dir_hint = report_arg.parent
    report_dir_hint.mkdir(parents=True, exist_ok=True)
    loaded_dirs, loaded_files, loaded_report = load_report(report_arg)
    dir_actions = loaded_dirs
    file_actions = loaded_files
    report_meta = loaded_report
else:
    existing_names: dict[str, Path] = {}
    existing_sigs: dict[tuple[int, str], Path] = {}
    for p in comic_files():
        try:
            existing_names.setdefault(normalize_filename(clean_name(clean_title(p.name))), p)
            if p.stat().st_size > 0:
                existing_sigs.setdefault(file_sig(p), p)
        except Exception:
            continue

    dir_actions = []
    file_actions = []
    report_meta = {}

    for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
        if d == root or d.name in ignored_dir_names:
            continue
        try:
            entries = list(d.iterdir())
        except FileNotFoundError:
            continue
        comics = [p for p in entries if p.is_file() and p.suffix.lower() in comic_exts]
        hidden = [p for p in entries if p.name.startswith(".")]
        other_files = [p for p in entries if p.is_file() and p.suffix.lower() not in comic_exts]
        child_dirs = [p for p in entries if p.is_dir()]

        if not entries:
            dir_actions.append(DirAction(d, "remove_empty_dir", "empty"))
            continue

        if not comics and other_files and not hidden and not child_dirs:
            dir_actions.append(
                DirAction(
                    d,
                    "archive_wrapper",
                    f"{len(entries)} entries, wrapper-like, no comic files",
                )
            )
        elif not comics and (other_files or hidden or child_dirs):
            dir_actions.append(
                DirAction(
                    d,
                    "quarantine_review_dir",
                    "preserve provenance; needs manual review",
                )
            )
        elif not comics and child_dirs and not other_files:
            dir_actions.append(
                DirAction(
                    d,
                    "keep_dir",
                    f"{len(child_dirs)} subdirs, no comic files in this level",
                )
            )

    comic_list = list(comic_files())
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(inspect_comic, p) for p in comic_list]
            for fut in as_completed(futures):
                action = fut.result()
                if action is not None:
                    file_actions.append(action)
    else:
        for p in comic_list:
            action = inspect_comic(p)
            if action is not None:
                file_actions.append(action)

    report_meta = {}


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


timestamp = time.strftime("%Y-%m-%d_%H%M%S")
report_dir.mkdir(parents=True, exist_ok=True)
report_path = report_dir / f"file_cleanup_{timestamp}.json"
end_epoch = time.time()
end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(end_epoch))

report = {
    "root": str(root),
    "mode": "apply" if apply_changes else "dry-run",
    "start_time": start_iso,
    "end_time": end_iso,
    "elapsed_seconds": round(end_epoch - start_epoch, 3),
    "workers": workers,
    "report_source": str(report_arg) if report_arg else None,
    "directory_actions": [
        {"path": str(action.path), "kind": action.kind, "detail": action.detail}
        for action in dir_actions
    ],
    "file_actions": [
        {"src": str(action.src), "dst": str(action.dst), "reason": action.reason, "detail": action.detail}
        for action in file_actions
    ],
    "summary": {
        "directory_actions": len(dir_actions),
        "file_actions": len(file_actions),
        "empty_dirs": sum(1 for action in dir_actions if action.kind == "remove_empty_dir"),
        "archive_wrappers": sum(1 for action in dir_actions if action.kind == "archive_wrapper"),
        "review_dirs": sum(1 for action in dir_actions if action.kind == "quarantine_review_dir"),
        "duplicate_files": sum(1 for action in file_actions if action.reason.startswith("duplicate")),
        "corrupt_or_empty": sum(1 for action in file_actions if action.reason in {"zero_length", "corrupt_archive"}),
    },
}

report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(f"root={root}")
print(f"mode={'apply' if apply_changes else 'dry-run'}")
print(f"workers={workers}")
print(f"start_time={start_iso}")
print(f"end_time={end_iso}")
print(f"elapsed_seconds={round(end_epoch - start_epoch, 3)}")
if report_arg:
    print(f"report_source={report_arg}")
print(f"report={report_path}")
if report_arg:
    print(f"report_source={report_arg}")
print("directory_actions=")
for action in dir_actions:
    print(f"  {action.kind}: {action.path} ({action.detail})")
print("file_actions=")
for action in file_actions:
    print(f"  {action.reason}: {action.src} -> {action.dst} ({action.detail})")

if not apply_changes:
    raise SystemExit(0)

archive_dir.mkdir(parents=True, exist_ok=True)
duplicate_dir.mkdir(parents=True, exist_ok=True)
quarantine_dir.mkdir(parents=True, exist_ok=True)
error_dir.mkdir(parents=True, exist_ok=True)
archive_meta_dir.mkdir(parents=True, exist_ok=True)

applied_dir = 0
applied_file = 0
skipped_missing = 0

for action in dir_actions:
    if not action.path.exists():
        print(f"skip_missing_dir: {action.path}", file=sys.stderr)
        skipped_missing += 1
        continue
    if action.kind == "remove_empty_dir":
        try:
            action.path.rmdir()
            applied_dir += 1
        except OSError:
            pass
    elif action.kind == "archive_wrapper":
        rel = action.path.relative_to(root)
        tar_name = archive_dir / (str(rel).replace("/", "_") + ".tar.gz")
        meta_name = archive_meta_dir / (str(rel).replace("/", "_") + ".json")
        ensure_parent(tar_name)
        ensure_parent(meta_name)
        meta_name.write_text(
            json.dumps(
                {
                    "source": str(action.path),
                    "archive": str(tar_name),
                    "detail": action.detail,
                    "root": str(root),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        with tarfile.open(tar_name, "w:gz") as tf:
            tf.add(action.path, arcname=rel)
        shutil.move(str(action.path), str(action.path.parent / f"{action.path.name}.archived"))
        applied_dir += 1
    elif action.kind == "quarantine_review_dir":
        target = quarantine_dir / "directories" / action.path.relative_to(root)
        ensure_parent(target)
        shutil.move(str(action.path), str(target))
        applied_dir += 1

for action in file_actions:
    if not action.src.exists():
        print(f"skip_missing_file: {action.src}", file=sys.stderr)
        skipped_missing += 1
        continue
    ensure_parent(action.dst)
    try:
        shutil.move(str(action.src), str(action.dst))
        applied_file += 1
    except Exception as exc:
        print(f"move_failed: {action.src} -> {action.dst}: {exc}", file=sys.stderr)

print(f"applied_dir_actions={applied_dir}")
print(f"applied_file_actions={applied_file}")
print(f"skipped_missing={skipped_missing}")
print("cleanup_complete=1")
PY
