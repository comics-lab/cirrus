# Imported Mylar Utilities — Post-Download Review

These files were copied from `/home/rmleonard/Projects/mylar-library/utilities/` as references for Cirrus post-download pipeline design.

Included:
- `PATCH_KAVITA_MYLAR_NOTES.md`: filename/folder-format guidance for Kavita/Mylar compatibility
- `README_KAVITA_VS_MYLAR3_STRUCTURE.md`: notes on scanner-friendly Mylar output structure
- `TODO_refactor_and_metadata_plan.md`: broader roadmap; not a direct deployment artifact
- `run_manual_import_batches.py`: batch-staging and Mylar post-process trigger script
- `api_metatag_series.py`: bulk/group metatag API trigger
- `api_rename_series.py`: bulk rename API trigger
- `verify_mylar_db_for_missing_metadata.py`: audit helper for matching missing metadata files against Mylar DB

Not copied:
- large sample/archive trees
- generated CSV/log artifacts
- one-off migration scripts unrelated to the current Cirrus intake boundary
- `api_metatag_missing.py`, which appears malformed and should be reviewed in the source repo before reuse

Current Cirrus interpretation:
- keep JDownloader as intake-only
- use these files as references for the next post-download split, not as ready-to-run production code
