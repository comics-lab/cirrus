# Utility Classification — 2026-04-01

## High-Level Findings
- `~/Projects/mylar-library/mylar.db` passed `PRAGMA integrity_check` and is structurally valid.
- The old Mylar environment may still be behaviorally broken because of config/code drift, but the database is not obviously corrupt.
- The `mylar-library/utilities` tree contains many viable scripts, but they mix reusable pipeline pieces with one-off migration jobs and path-specific operational debris.
- The `comics-lab` tree contains a few useful reference projects, but several of the most promising metadata packages are still CLI stubs.
- The most useful immediate path is to build a new Cirrus-native post-download toolkit from the working pieces rather than trying to rehabilitate the whole legacy Mylar utility pile.

## Immediate Keepers For Adaptation
These are the strongest candidates to adapt into the new Cirrus workflow.

### Archive Conversion / Validation
- `convert_cbr_to_cbz.py`
  - Good base for a CBR -> CBZ converter.
  - Uses `7z` extract/test cycle and stages originals after successful conversion.
  - Needs path/config cleanup and better relative-path handling.
- `cbz_verify.py`
  - Good simple CBZ integrity checker using Python `zipfile`.
  - Currently hardcoded to `/mnt/grackle/LIBRARY`.
- `cbz_metadata_audit.py`
  - Good archive metadata audit for `ComicInfo.xml` / `MetronInfo.xml` at root vs nested.
  - Useful as a first pass in the intake pipeline.
- `preimport_cleaner.py`
  - Good early triage tool for `clean / review / broken` classification.
  - Filename heuristics are rough, but the control flow is sound.

### Metadata / Mylar Interop
- `api_metatag_series.py`
  - Structurally sound helper for Mylar metatag endpoints.
  - Useful once the new Mylar deployment exists and is healthy.
- `api_rename_series.py`
  - Structurally sound helper for Mylar rename endpoints.
  - Also useful after Mylar is deployed and verified.
- `verify_mylar_db_for_missing_metadata.py`
  - Useful audit helper that compares missing metadata reports against Mylar DB rows.
- `run_manual_import_batches.py`
  - Useful as a pattern for staged batch submission into Mylar post-processing.
  - Strong path and URL assumptions must be removed.

## Useful But Requires Heavy Rework
These contain real value, but should be treated as reference code rather than near-drop-in utilities.

- `gcd_comicinfo_seed.py`
  - Useful for building baseline `ComicInfo.xml` from GCD + `series.json`.
  - Not sufficient for the target workflow because it does not populate ComicVine IDs.
  - Script also points at an outdated embedded GCD DB path under `utilities/`.
- `metroninfo_fill.py`
  - Potentially useful for writing `MetronInfo.xml` through Darkseid/Metron libraries.
  - Hardcodes local library paths and external project imports.
  - Best treated as a design reference for a new Cirrus-native writer.
- `combined_importer.py`
  - Contains valuable ideas for Mylar API + DB-assisted import resolution.
  - Too entangled with legacy helpers, old API base URLs, and old Mylar assumptions to adopt directly.
- `cv_comicinfo_seed.py`
  - Likely relevant to ComicVine-backed seeding, but should be reviewed after the Cirrus-native metadata model is defined.
- `comicinfo_fill_from_seriesjson.py`
  - May help with fallback metadata population, but is tied to old sidecar assumptions.
- `metron_to_comicinfo.py`
  - Potentially useful bridge logic, but should be reviewed only after deciding canonical metadata precedence.
- `detect_missing_metadata.py`
  - Probably useful in the audit stage, but likely needs to be folded into a consolidated verifier.
- `look4untaggedcbzs.py`
  - Candidate for consolidation into a single audit command rather than retained as a standalone tool.

## Broken Or Do Not Reuse Directly
- `api_metatag_missing.py`
  - Currently malformed: Python syntax error.
  - Do not reuse without repair.
- `test.sh`
  - Not a real shell utility; appears to contain stray text.
- `rename_plan_fearless.sh`
- `rename_plan_grackle.sh`
- `rename_exec_fearless.sh`
- `rename_exec_grackle.sh`
  - Syntax is fine, but they are path- and library-specific rename jobs tied to old storage layouts.
  - Do not bring these into the new Cirrus workflow.
- `start_codex.sh`
- `start_mylar.sh`
  - Operational launchers, not pipeline utilities.

## Likely Reference-Only / One-Off Legacy Jobs
These may contain ideas but are not first-class candidates for the new pipeline.
- `archived_missing_to_wanted.py`
- `audit_comics.py`
- `black_hammer_import.py`
- `build_asm_chrono_hc_2026.py`
- `cbr_bad_scan_move.py`
- `cbr_rebuild_queue.py`
- `cbz_metadata_audit_seriesjson.py`
- `compare_filename_parsers.py`
- `compare_importers.py`
- `dry_run_classify_elsewhere.py`
- `generate_library_missing_from_wanted.py`
- `lightweight_filename_parser.py`
- `merge_cbr_conversion_reports.py`
- `move_archived_found_elsewhere.py`
- `normalize_blackhammer_filenames.py`
- `process_bad_archives.py`
- `queue_missing_issues.py`
- `reconcile_library_vs_db.py`
- `resume_duplicate_moves.py`
- `retry_cbr_extracts.py`
- `run_cbr_conversion_queue.py`
- `stage_bad_cbz.py`
- `stage_cbr_duplicates.py`
- `stage_duplicates.py`

## Shell Script Classification
### Worth Mining For Logic
- `look4cbrs.sh`
- `batch_poller.sh`
- `recheck_files_batches_2026-02-06.sh`
- `recheck_files_quick_5.sh`
- `run_phase123_then_pause.sh`
- `status_snapshot.sh`

### Legacy / Path-Specific / Operational Only
- `rename_*_fearless.sh`
- `rename_*_grackle.sh`
- `start_codex.sh`
- `start_mylar.sh`
- `test.sh`

## `comics-lab` Classification
### Most Useful Reference Projects
- `comictagger/`
  - Real, mature archive/tagging code.
  - Strong reference for archive handling, filename parsing, and `ComicInfo.xml` logic.
- `mylar3/`
  - Real upstream/reference application code.
  - Use for understanding post-processing, metatagging, and import expectations.
- `comic-file-organizer/`
  - Contains real scanner/statistics code for Mylar-style library layouts.
  - Useful for library scanning assumptions and path structure, not for direct metadata writing.
- `comicmeta-comicvine/`
  - Client code exists and looks real.
  - CLI is still a stub.
  - Best used as a library/reference, not as a ready command.

### Currently Mostly Stubs / Not Yet Productive
- `cbz-doctor/`
  - CLI stub.
- `comicmeta-gcd/`
  - CLI stub.
- `comicmeta-metron/`
  - CLI stub.
- `mylar3-sanity/`
  - CLI stub.

## GCD Data Status
Found under:
- `/home/rmleonard/Projects/GCD_Current_Database`

Available artifacts:
- `2025-03-15.db`
- `GCD_current_03-23-2025.zip`
- `GCD_current_2025-10-15.zip`
- `GCD-03-29-2026.zip`

Interpretation:
- There is clearly usable GCD source data locally.
- The existing utility scripts still point at old utility-local DB paths and should be repointed to this canonical dataset location.

## Recommended New Pipeline Shape
1. `cbr_to_cbz`
   - based on `convert_cbr_to_cbz.py`
2. `archive_verify`
   - based on `cbz_verify.py`
3. `metadata_audit`
   - based on `cbz_metadata_audit.py`
4. `metadata_enrich`
   - new utility combining GCD + ComicVine + Metron references
5. `route_to_import`
   - only items with valid `ComicInfo.xml` including ComicVine identifiers go to Mylar import staging
6. `route_to_review`
   - missing/bad metadata, unreadable archives, and ambiguous naming go to alternate review queues

## Immediate Next Development Work
- Build a Cirrus-native `cbr_to_cbz` utility first.
- Build a Cirrus-native `cbz_audit` utility second.
- Define exactly what counts as a valid `ComicInfo.xml` for Mylar import.
- Only after that, decide whether to adapt pieces of the Mylar API helpers or replace them entirely.
