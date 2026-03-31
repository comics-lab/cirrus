#!/usr/bin/env python3
"""Trigger Mylar manualRename for series via web endpoint.

Uses Mylar DB to fetch ComicIDs and calls /manualRename with batches.
"""

import argparse
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path


def fetch_comic_ids(db_path: Path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT ComicID FROM comics ORDER BY ComicID")
    ids = [row["ComicID"] for row in cur.fetchall()]
    con.close()
    return ids


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]


def call_manual_rename(base_url, comic_ids):
    params = []
    for cid in comic_ids:
        params.append(("comicid", str(cid)))
    url = f"{base_url.rstrip('/')}/manualRename?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        body = resp.read(200).decode("utf-8", errors="replace")
    return resp.status, body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default="/home/rmleonard/Projects/mylar-library/mylar.db")
    ap.add_argument("--base-url", default="http://127.0.0.1:8690/library")
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ids = fetch_comic_ids(Path(args.db_path))
    if args.limit:
        ids = ids[:args.limit]

    total = len(ids)
    print(f"total_series={total}")

    for idx, batch in enumerate(chunked(ids, args.batch_size), start=1):
        if args.dry_run:
            print(f"dry_run batch {idx}: {batch}")
        else:
            status, body = call_manual_rename(args.base_url, batch)
            print(f"batch {idx} status {status} body {body}")
        time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
