# Cirrus Utilities

This directory contains Cirrus-native utility scripts for the current
post-download pipeline.

These utilities should prefer:

- current Cirrus paths over legacy `grackle` / `fearless` assumptions
- explicit staging and report paths
- dry-run support where practical
- simple, inspectable behavior over hidden automation

Current utilities:

- `cbr_to_cbz.py`: convert `.cbr` archives under intake roots into `.cbz`,
  verify the new archive, and stage originals separately after success
- `cbz_audit.py`: inspect `.cbz` intake archives for root vs nested
  `ComicInfo.xml` / `MetronInfo.xml`, basic XML parseability, upstream-Mylar
  ComicVine reference detection from `Notes` and `Web`, and first-pass
  `mylar_import_valid` classification
- `cv_issue_resolver.py`: query ComicVine for likely issue IDs based on
  existing root `ComicInfo.xml`, archive filenames, and parent directory
  names; emits a CSV report and conservatively classifies results as
  `resolved`, `candidate`, or `unresolved` before any ComicTagger write pass
- `pass1_write_comicinfo.py`: initial Pass 1 wrapper that re-audits files,
  skips anything already Mylar-valid or labeled `WebP`, resolves likely
  ComicVine issue IDs, and only attempts ComicTagger writes for `resolved`
  matches
- `promote_mylar_import.py`: move already-Mylar-valid archives from intake
  into `/mnt/phoenix/media/incoming/mylar-import` without touching candidate
  or unresolved files
- `verify_weekly_pack_extracts.py`: compare non-`WebP` weekly-pack zip files
  against their same-named extracted publisher directories and report which
  packs are trustworthy as a larger test corpus
- `rebuild_quarantine_cbz.py`: rebuild normalized `.cbz` files from extracted
  image folders under `/mnt/phoenix/media/incoming/cbr-quarantine`, verify the
  rebuilt archive, and delete the extracted working folder only after success
- `mylar_paced_import.py`: slowly stage pre-tagged `.cbz` files into Mylar one
  at a time, call `forceProcess` for a dedicated queue directory, and log
  consumed vs rejected items so bulk imports can be throttled conservatively
- `mylar_series_import.py`: import pre-organized series directories that
  already carry `series.json` ComicVine volume ids by adding each series to
  Mylar, copying issue files into the watched series folder, then calling
  `recheckFiles` followed by `manualRename`
