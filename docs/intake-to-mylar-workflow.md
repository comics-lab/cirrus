# Intake To Mylar Workflow

This is the current Cirrus operator workflow for taking files from:

- `/mnt/phoenix/media/incoming/jdownloader`

and getting them into:

- `/mnt/phoenix/media/incoming/mylar-import`

so Mylar3 can automatically consume them.

The rule is simple:

- raw intake stays in `jdownloader`
- only archives that are already ready for Mylar go into `mylar-import`
- anything ambiguous goes to manual review first

## Working Directory

Run the scripts from the Cirrus repo root:

```bash
cd /home/rmleonard/Projects/cirrus
```

Most utilities default to the current Cirrus paths, so you usually do not need to pass custom roots unless you are testing a subtree.

## End State

The intended final state for a file is:

1. a clean `.cbz`
2. rooted `ComicInfo.xml`
3. a ComicVine reference in `Notes` or `Web`
4. `mylar_import_valid == 1` from `utilities/cbz_audit.py`
5. moved into `/mnt/phoenix/media/incoming/mylar-import`

If a file is not ready for that state, do not stage it into `mylar-import`.

## Script Order

Use the scripts in this order:

1. extract `.zip` payloads
2. convert `.cbr` to `.cbz`
3. run pre-pass normalization on files with local sidecars or cache matches
4. audit the resulting `.cbz`
5. run Pass 1 only on high-confidence matches
6. promote `mylar_valid` files into `mylar-import`
7. let Mylar import from `mylar-import`

## 1. Extract Zip Payloads

Script:

- `utilities/extract_zip_payloads.py`

Default command:

```bash
python3 utilities/extract_zip_payloads.py
```

What it does:

- scans `/mnt/phoenix/media/incoming/jdownloader`
- extracts `.cbz`, `.cbr`, and `.pdf` entries from `.zip` files
- skips entries with `webp` in the name
- moves processed zips into `/mnt/phoenix/media/incoming/archive`
- if a zip filename itself contains `webp`, it is left in place and not archived
- if the extracted payload would exceed available space on the target filesystem, the zip is left in place and not archived

For weekly packs or other alternate roots, pass the root explicitly:

```bash
python3 utilities/extract_zip_payloads.py --root /mnt/phoenix/media/incoming/weekly-lots
```

Useful options:

```bash
python3 utilities/extract_zip_payloads.py --dry-run
python3 utilities/extract_zip_payloads.py --limit 10
python3 utilities/extract_zip_payloads.py --root /path/to/other/root
```

Likely errors:

- `BadZipFile`
  - the archive is corrupt or not really a zip
  - leave it in place and inspect manually
- `no_payloads`
  - the zip only contained files that were skipped or non-comic payloads
  - leave it in place or archive it only if the contents were already expanded elsewhere
- `error`
  - unexpected extraction failure
  - inspect the report and the archive before retrying

## 2. Convert CBR To CBZ

Script:

- `utilities/cbr_to_cbz.py`

Default command:

```bash
python3 utilities/cbr_to_cbz.py
```

What it does:

- scans `/mnt/phoenix/media/incoming/jdownloader`
- recursively finds `.cbr`
- extracts each archive with `unar` first, then `7z` as fallback
- rebuilds a clean `.cbz`
- moves the original `.cbr` into staging only after the new `.cbz` verifies cleanly

Useful options:

```bash
python3 utilities/cbr_to_cbz.py --dry-run
python3 utilities/cbr_to_cbz.py --limit 25
python3 utilities/cbr_to_cbz.py --extract-timeout 180
python3 utilities/cbr_to_cbz.py --root /path/to/other/root
```

Likely errors:

- `skip_exists`
  - a `.cbz` with the same name already exists
  - do not overwrite; compare or archive the duplicate
- `skip_no_space`
  - not enough free space on the target filesystem
  - leave the source archive in place and retry later after cleanup
- `extract_failed_corrupt`
  - the raw archive is probably damaged
  - quarantine it and inspect with another tool or re-download if needed
- `extract_failed_unsupported`
  - the extractor does not support that compression method
  - retry with fallback tooling or quarantine for manual repair
- `verify_failed`
  - extraction succeeded but the rebuilt `.cbz` did not verify
  - do not promote it

## 3. Audit CBZ Readiness

Script:

- `utilities/cbz_audit.py`

Default command:

```bash
python3 utilities/cbz_audit.py
```

What it does:

- scans `.cbz` under `/mnt/phoenix/media/incoming/jdownloader`
- checks for root and nested `ComicInfo.xml` / `MetronInfo.xml`
- parses root `ComicInfo.xml`
- looks for ComicVine references in `Notes` and `Web`
- marks files `mylar_import_valid` only when:
  - root `ComicInfo.xml` parses
  - `Series` exists
  - `Number` exists
  - a ComicVine reference is recoverable

Useful options:

```bash
python3 utilities/cbz_audit.py --limit 50
python3 utilities/cbz_audit.py --root /path/to/other/root
python3 utilities/cbz_audit.py --report /tmp/custom_audit.csv
```

Likely outcomes:

- `mylar_import_valid = 1`
  - safe to promote
- `comicinfo_parse_ok = 1` but no ComicVine reference
  - good candidate for manual metadata work, but not ready for Mylar automation
- missing `Series` or `Number`
  - not ready for Mylar import
- `BadZipFile`
  - archive is broken or mislabeled

## 4. Pre-Pass Normalization

Script:

- `utilities/prepass_normalize.py`

Default command:

```bash
python3 utilities/prepass_normalize.py
```

What it does:

- scans `.cbz` under the intake root
- reads local `series.json` and root `ComicInfo.xml`
- consults the local CBL lookup cache
- when the match is strong, moves the file into a publisher/series folder
- writes rooted `ComicInfo.xml`
- writes rooted `MetronInfo.xml`
- emits a CSV report of normalized vs manual-review files

Useful options:

```bash
python3 utilities/prepass_normalize.py --root /mnt/phoenix/media/incoming/jdownloader
python3 utilities/prepass_normalize.py --cache-db /home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3
python3 utilities/prepass_normalize.py --report /tmp/prepass.csv
```

Likely outcomes:

- `normalize_ready`
  - strong local match; file was moved and rewritten
- `manual_review`
  - no strong local match
  - leave it in intake or move to review
- `target_exists`
  - destination file already exists
  - inspect before retrying

## 5. Pass 1 Metadata Writing

Script:

- `utilities/pass1_write_comicinfo.py`

Default command:

```bash
python3 utilities/pass1_write_comicinfo.py
```

What it does:

- scans intake `.cbz`
- skips files already Mylar-valid
- skips anything labeled `WebP`
- resolves likely ComicVine issue ids
- only writes tags for `resolved` matches
- re-audits after writing

Useful options:

```bash
python3 utilities/pass1_write_comicinfo.py --limit 20
python3 utilities/pass1_write_comicinfo.py --dry-run
python3 utilities/pass1_write_comicinfo.py --root /mnt/phoenix/media/incoming/jdownloader
```

Likely resolver states:

- `resolved`
  - write can proceed
- `candidate`
  - too weak for blind auto-write
  - move to manual review
- `unresolved`
  - no safe match
  - move to manual review or leave in intake
- `error`
  - resolver or ComicVine lookup failed
  - retry later or inspect the report

Important note:

- the script uses a working ComicTagger CLI and is intentionally conservative
- do not force `candidate` or `unresolved` rows into automatic tagging unless you have manually verified them

## 6. Promote Ready Files Into Mylar Import

Script:

- `utilities/promote_mylar_import.py`

Default command:

```bash
python3 utilities/promote_mylar_import.py
```

What it does:

- re-audits `.cbz` under the source root
- moves only files already `mylar_import_valid`
- places them in `/mnt/phoenix/media/incoming/mylar-import`

Useful options:

```bash
python3 utilities/promote_mylar_import.py --dry-run
python3 utilities/promote_mylar_import.py --limit 20
python3 utilities/promote_mylar_import.py --root /path/to/source
python3 utilities/promote_mylar_import.py --dest /mnt/phoenix/media/incoming/mylar-import
```

Likely outcomes:

- `moved = 1`
  - file is now staged for Mylar
- `not_mylar_valid`
  - leave it out of `mylar-import`
- `skipped_webp`
  - ignore or handle separately

## 7. Mylar Import

Mylar watches:

- `/mnt/phoenix/media/incoming/mylar-import`

The container is already configured to use:

- `/mylar-imports`

Mylar should then process the staged files on its normal scan interval.

If Mylar reports:

- `No books to import`
  - the files are not sufficiently importable for the scan path
  - re-audit them and make sure they are truly `mylar_import_valid`
- repeated scans without draining the basket
  - the basket probably contains already-known duplicates or non-matchable files
  - move those out of `mylar-import`

## Error Handling Rules

When a script fails:

1. check the CSV report it produced
2. distinguish between:
   - archive corruption
   - no payloads
   - unsupported extraction
   - missing ComicVine metadata
   - weak resolver result
3. quarantine or manually review only the files that need it
4. do not keep rerunning the same broken batch without changing the input set

Common failure patterns:

- zip already expanded elsewhere
  - move the zip into archive
  - do not try to extract it again
- cbr converted badly
  - quarantine the raw archive and inspect the rebuild
- file has `ComicInfo.xml` but no ComicVine id
  - good for manual metadata, not ready for Mylar automation
- Mylar keeps skipping the file
  - likely duplicate or already-complete series behavior
  - move it out of the active basket

## Practical Recommended Flow

For normal intake batches, use this sequence:

1. `extract_zip_payloads.py`
2. `cbr_to_cbz.py`
3. `cbz_audit.py`
4. `pass1_write_comicinfo.py`
5. `promote_mylar_import.py`
6. Mylar auto-import from `/mylar-imports`

If a batch is obviously ambiguous, skip step 4 and send it to manual review instead.
