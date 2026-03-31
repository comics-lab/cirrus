#!/usr/bin/env python3
import csv
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


SOURCE_ROOT = Path("/home/Various-Downloads/Various")
STAGING_ROOT = Path("/home/Various-Downloads/Various/_holding/manual_import_batches_2026-01-31")
LOG_DIR = Path("/home/rmleonard/Projects/mylar-library/utilities")
MYLAR_BASE = "http://localhost:8690/library"


def find_archives(limit):
    archives = []
    for dirpath, _, filenames in os.walk(SOURCE_ROOT):
        # skip staging area
        if Path(dirpath).resolve().is_relative_to(STAGING_ROOT.resolve()):
            continue
        for fn in filenames:
            if fn.lower().endswith((".cbr", ".cbz")):
                archives.append(Path(dirpath) / fn)
                if len(archives) >= limit:
                    return archives
    return archives


def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)


def trigger_post_process(folder):
    params = f"nzb_name=Manual+Run&nzb_folder={folder.as_posix()}&failed=0"
    url = f"{MYLAR_BASE}/post_process?{params}"
    return subprocess.run(["curl", "-s", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    total_batches = 10
    batch_size = 25
    total_needed = total_batches * batch_size

    ensure_dir(STAGING_ROOT)

    moved_log = LOG_DIR / "manual_import_batches_moved.csv"
    trigger_log = LOG_DIR / "manual_import_batches_trigger.csv"

    archives = find_archives(total_needed)
    if len(archives) < total_needed:
        print(f"Only found {len(archives)} archives (needed {total_needed}). Proceeding with available files.")

    # Move into batch folders
    moved_rows = []
    for i in range(total_batches):
        batch_idx = i + 1
        batch_folder = STAGING_ROOT / f"batch_{batch_idx:02d}"
        ensure_dir(batch_folder)
        for j in range(batch_size):
            idx = i * batch_size + j
            if idx >= len(archives):
                break
            src = archives[idx]
            dst = batch_folder / src.name
            try:
                shutil.move(str(src), str(dst))
                moved_rows.append([str(src), str(dst), "moved", ""])
            except Exception as e:
                moved_rows.append([str(src), str(dst), "error", str(e)])

    with moved_log.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src", "dst", "status", "error"])
        w.writerows(moved_rows)

    # Trigger post-processing per batch folder
    trigger_rows = []
    for i in range(total_batches):
        batch_folder = STAGING_ROOT / f"batch_{i+1:02d}"
        if not batch_folder.exists():
            continue
        res = trigger_post_process(batch_folder)
        trigger_rows.append([
            batch_folder.as_posix(),
            res.returncode,
            res.stdout.decode(errors="ignore").strip(),
            res.stderr.decode(errors="ignore").strip()
        ])

    with trigger_log.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["batch_folder", "curl_rc", "stdout", "stderr"])
        w.writerows(trigger_rows)

    summary = LOG_DIR / "manual_import_batches_summary.txt"
    summary.write_text(
        "Manual import batches triggered {}\n"
        "Staging root: {}\n"
        "Moved log: {}\n"
        "Trigger log: {}\n".format(
            datetime.now().isoformat(),
            STAGING_ROOT,
            moved_log,
            trigger_log,
        )
    )
    print(summary.read_text())


if __name__ == "__main__":
    main()
