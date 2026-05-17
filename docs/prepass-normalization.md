# Pre-Pass Normalization

This is the stage that comes before `pass1_write_comicinfo.py`.

Its job is to use local hints already present in the file tree:

- `series.json`
- root `ComicInfo.xml`
- the local CBL reading-list cache

The goal is to validate and normalize files before they are handed to Pass 1.

## Why This Exists

Pass 1 is good at final ComicVine resolution and tagging.

It is not the right place to:

- guess obvious file naming conventions
- decide whether a file belongs to a known series using local sidecars
- normalize archive names
- build library-side metadata like `MetronInfo.xml`

Those are pre-pass tasks.

## Script

The first normalization script is:

- `utilities/prepass_normalize.py`

Current behavior:

- scans `.cbz` under a source root
- reads root `ComicInfo.xml` when present
- reads `series.json` from the parent chain when present
- consults the local CBL cache
- emits a report of strong matches vs manual-review files

Default command:

```bash
python3 utilities/prepass_normalize.py
```

Useful options:

```bash
python3 utilities/prepass_normalize.py --root /mnt/phoenix/media/incoming/jdownloader
python3 utilities/prepass_normalize.py --cache-db /home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3
python3 utilities/prepass_normalize.py --report /tmp/prepass.csv
```

## Next Intended Evolution

Once the pre-pass is stable, it should grow to:

1. rename files into a consistent Cirrus naming convention
2. create or update `ComicInfo.xml`
3. create or update `MetronInfo.xml`
4. stage only strong matches into the next pass

Then Pass 1 can do the final ComicVine issue-id completion.

## Failure Handling

If the pre-pass cannot find a strong local match:

- do not rename the file
- do not write metadata
- leave it in intake or move it to manual review

Likely reasons:

- no `series.json`
- missing root `ComicInfo.xml`
- ambiguous issue number
- local cache has multiple possible matches
- the file is an alternate edition or special
