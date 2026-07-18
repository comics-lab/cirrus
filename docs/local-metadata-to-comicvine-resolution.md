# Local Metadata To ComicVine Resolution

This workflow uses cleaner local metadata from GCD and Metron to recover the
best ComicVine issue id for ambiguous or relaunch-heavy records.

Scripts:

- `utilities/resolve_issue_from_local_metadata.py`
- `scripts/resolve_issue_from_local_metadata.sh`

Inputs:

- `series`
- `issue`
- `year`
- `publisher`
- `title`
- GCD SQLite metadata at `mylar-library/utilities/2025-10-15.db`
- existing cache rows in `data/cbl_lookup.sqlite3`

Behavior:

- prefers local GCD metadata when it can match series name, publisher, and
  year
- uses the existing ComicVine resolver scoring helpers
- writes a review CSV instead of changing the cache

Example:

```bash
./scripts/resolve_issue_from_local_metadata.sh \
  /mnt/phoenix/media/incoming/jdownloader \
  /home/rmleonard/Projects/cirrus/data/reports/resolve_issue_review.csv \
  10
```

For a manual single-record check, omit `--root` in the Python utility and pass
`--series`, `--issue`, `--year`, `--publisher`, and `--title` directly.
