#!/usr/bin/env python3
import argparse
import csv
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Path to mylar.db")
    parser.add_argument("--audit", required=True, help="Audit CSV with cbz_path")
    parser.add_argument("--out", required=True, help="CSV output")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    out_rows = []
    with open(args.audit, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cbz = r["cbz_path"]
            # Only include missing or misplaced comicinfo
            if not (r["comicinfo_in_subfolders"] == "1" or (r["has_comicinfo_root"] == "0" and r["has_metroninfo_root"] == "0")):
                continue
            basename = Path(cbz).name
            cur.execute("SELECT ComicID, ComicName, Issue_Number, Status, Location FROM issues WHERE Location = ?", (basename,))
            rows = cur.fetchall()
            if rows:
                if len(rows) == 1:
                    row = rows[0]
                    out_rows.append(
                        {
                            "cbz_path": cbz,
                            "db_found": 1,
                            "ComicID": row[0],
                            "ComicName": row[1],
                            "Issue_Number": row[2],
                            "Status": row[3],
                            "Location": row[4],
                        }
                    )
                else:
                    out_rows.append(
                        {
                            "cbz_path": cbz,
                            "db_found": 2,
                            "ComicID": ",".join(r[0] for r in rows),
                            "ComicName": ",".join(r[1] for r in rows),
                            "Issue_Number": ",".join(str(r[2]) for r in rows),
                            "Status": ",".join(r[3] for r in rows),
                            "Location": basename,
                        }
                    )
            else:
                out_rows.append(
                    {
                        "cbz_path": cbz,
                        "db_found": 0,
                        "ComicID": "",
                        "ComicName": "",
                        "Issue_Number": "",
                        "Status": "",
                        "Location": "",
                    }
                )

    conn.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["cbz_path", "db_found", "ComicID", "ComicName", "Issue_Number", "Status", "Location"],
        )
        writer.writeheader()
        writer.writerows(out_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
