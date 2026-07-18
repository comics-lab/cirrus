# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-07-07)
- The intake pipeline is being consolidated into a single Python orchestrator that starts after `cbr_to_cbz`.
- Cleanup is now report-driven and replay-based.
- `prepass_normalize.py` now has a fallback path for non-ComicVine identifiers, and it can still write both `ComicInfo.xml` and `MetronInfo.xml`.
- `pass1_batch.sh` and `pass1_then_promote.sh` now default to the live `.cbz` count instead of a hardcoded 500.
- `file_cleanup_parallel.sh` now defaults to `nproc`.
- `utilities/intake_pipeline.py` is the current high-level entrypoint for the post-conversion flow.
- The current hardware model to remember:
  - `/dev/md0` is the local NVMe Btrfs array
  - `/dev/sda` is a USB3 volume
  - other `/mnt/*` mounts are NFS
  - zram may be active
  - the host has 16 GiB RAM

## Start With
- `README.md`
- `RESUME.md`
- `docs/pipeline-v2-notes.md`
- `docs/transfer-load.md`
- `docs/intake-to-mylar-workflow.md`
- `utilities/intake_pipeline.py`

## Important References
- `docs/pipeline-v2-notes.md`
- `docs/transfer-load.md`
- `docs/intake-to-mylar-workflow.md`
- `logical_storage.md`
- `hardening.md`
- `cirrus_checklist.md`

## Open Questions
- Which stage should become fully inlined next: cache rebuild, prepass normalization, or cleanup replay?

## Next Recommended Work
1. Let the current intake pipeline finish on the live JDownloader set and review whether the fallback prepass improves promotion yield.
2. Decide whether `utilities/intake_pipeline.py` should stop shelling out and own the stage logic directly.
3. Keep cleanup replay as the only report-driven apply step.
4. Keep the `nproc` worker default and the live `.cbz` count limit behavior.

## Practical Next Step
1. Return to the app/deployment track and pick up the next planned service work, starting with Immich deployment and phone/tablet migration planning.
2. Keep the Archie plain-series migration lane paused until there is a deliberate batch to process.
3. Keep JDownloader as the active raw intake queue and only promote files into `mylar-import` when they are true standalone candidates for Mylar folder processing.
