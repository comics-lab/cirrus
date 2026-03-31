#!/usr/bin/env python3
"""Trigger Mylar metatagging via web endpoints.

Uses Mylar DB to build per-series IssueID lists and calls group_metatag
or bulk_metatag in chunks (to respect CV batch limit threshold).
"""

import argparse
import configparser
import sqlite3
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


def load_threshold(config_path: Path, default=200):
    cp = configparser.ConfigParser()
    cp.read(config_path)
    try:
        return int(cp.get('Metatagging', 'cv_batch_limit_threshold', fallback=str(default)))
    except Exception:
        return default


def fetch_issue_ids(db_path: Path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    issues = defaultdict(list)
    cur.execute("SELECT ComicID, IssueID FROM issues WHERE Location IS NOT NULL")
    for row in cur.fetchall():
        issues[row["ComicID"]].append(row["IssueID"])
    cur.execute("SELECT ComicID, IssueID FROM annuals WHERE Location IS NOT NULL AND NOT Deleted")
    for row in cur.fetchall():
        issues[row["ComicID"]].append(row["IssueID"])
    con.close()
    return issues


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]


def call_endpoint(url, params):
    full = url + "?" + urllib.parse.urlencode(params, doseq=True)
    with urllib.request.urlopen(full, timeout=120) as resp:
        body = resp.read(200).decode("utf-8", errors="replace")
    return resp.status, body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default="/home/rmleonard/Projects/mylar-library/mylar.db")
    ap.add_argument("--config-path", default="/home/rmleonard/Projects/mylar-library/config.ini")
    ap.add_argument("--base-url", default="http://127.0.0.1:8690/library")
    ap.add_argument("--batch-size", type=int, default=0, help="Override CV batch limit; 0=use config")
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--limit-series", type=int, default=0)
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    threshold = args.batch_size or load_threshold(Path(args.config_path))
    issues = fetch_issue_ids(Path(args.db_path))
    comic_ids = sorted(issues.keys(), key=lambda x: int(x))

    if args.start_index:
        comic_ids = comic_ids[args.start_index:]
    if args.limit_series:
        comic_ids = comic_ids[:args.limit_series]

    print(f"series_count={len(comic_ids)} threshold={threshold}")

    for idx, comicid in enumerate(comic_ids, start=1):
        issue_ids = issues.get(comicid, [])
        if not issue_ids:
            continue
        if len(issue_ids) <= threshold:
            if args.dry_run:
                print(f"dry_run group_metatag ComicID={comicid} count={len(issue_ids)}")
            else:
                status, body = call_endpoint(f"{args.base_url.rstrip('/')}/group_metatag", {"ComicID": comicid})
                print(f"series {idx} group_metatag {comicid} status {status} body {body}")
        else:
            for chunk_idx, chunk in enumerate(chunked(issue_ids, threshold), start=1):
                if args.dry_run:
                    print(f"dry_run bulk_metatag ComicID={comicid} chunk={chunk_idx} count={len(chunk)}")
                else:
                    params = {"ComicID": comicid, "IssueIDs": [str(i) for i in chunk]}
                    status, body = call_endpoint(f"{args.base_url.rstrip('/')}/bulk_metatag", params)
                    print(f"series {idx} bulk_metatag {comicid} chunk {chunk_idx} status {status} body {body}")
                time.sleep(args.delay)
        time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
