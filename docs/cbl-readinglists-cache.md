# CBL Reading Lists Cache

The `Projects/CBL-ReadingLists/` tree contains XML `.cbl` reading lists that often include ComicVine-backed issue references.

This makes them useful as a local lookup cache for Pass 1 and other metadata work.

## What The Files Contain

A typical `.cbl` file is XML with:

- a reading list name
- a list of `<Book>` entries
- per-book `Series`, `Number`, `Volume`, and `Year`
- a `<Database Name="cv" Series="..." Issue="..." />` entry

That means the file is often already carrying the ComicVine series and issue ids we want to reuse locally.

## What We Cache

The Cirrus cache builder extracts:

- reading list file path
- reading list name
- book index within the list
- series name
- issue number
- volume year
- ComicVine series id
- ComicVine issue id

The resulting SQLite cache is:

- `/home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3`

The CSV report is written under:

- `/home/rmleonard/Projects/cirrus/data/reports`

## Cache Builder

Script:

- `utilities/build_cbl_cache.py`
- `utilities/cbl_cache_match_report.py`
- `utilities/cbl_cache_vs_library_report.py`

Default command:

```bash
python3 utilities/build_cbl_cache.py
```

Useful options:

```bash
python3 utilities/build_cbl_cache.py --dry-run
python3 utilities/build_cbl_cache.py --root ../CBL-ReadingLists
python3 utilities/build_cbl_cache.py --db /home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3
python3 utilities/cbl_cache_match_report.py --root ../CBL-ReadingLists
python3 utilities/cbl_cache_match_report.py --db /home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3
python3 utilities/cbl_cache_vs_library_report.py
python3 utilities/cbl_cache_vs_library_report.py --root /mnt/phoenix/media/comics --root /mnt/phoenix/media/incoming/mylar-import
```

## Why This Helps

The cache can speed up Pass 1 by letting us:

- match a series title against an already-known ComicVine series id
- reuse issue-level ComicVine ids when the reading list already knows them
- avoid repeated XML parsing of the same `.cbl` files

## Practical Use

The cache is a helper, not a source of truth.

Use it when a file title or series name already looks like a known reading-list match.
If the reading list is ambiguous or the issue number is unreliable, fall back to manual review or the normal resolver path.

`cbl_cache_match_report.py` is the report companion when you want counts instead of rebuilding the cache.
It tells you how many reading-list books are exact cache hits, series-only hits, ambiguous hits, or unmatched.

`cbl_cache_vs_library_report.py` compares the cached reading-list ComicVine ids against existing CBZ archives in the comics library and Mylar staging basket.
It tells you how many cached reading-list issues are already present versus still missing.
