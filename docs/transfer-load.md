# Transfer Load Instructions

Use this repo as the startup context for the next session.

## Load Order

1. Read `README.md`
2. Read `RESUME.md`
3. Read `docs/pipeline-v2-notes.md`
4. Read `docs/intake-to-mylar-workflow.md`
5. Read `scripts/refresh_intake_pipeline.sh`
6. Read `utilities/intake_pipeline.py`

## Current Working State

- Post-conversion intake is now being consolidated into a single Python orchestrator.
- Cleanup is report-driven and replay-based.
- `prepass_normalize.py` now has a fallback metadata path for non-ComicVine identifiers.
- `pass1_batch.sh` and `pass1_then_promote.sh` now default to the live `.cbz` count.
- `file_cleanup_parallel.sh` defaults to `nproc`.

## Resume Point

- The immediate next task is to decide whether the consolidated pipeline should fully inline the stage logic rather than shelling out.
- The next operational task is to let the current intake pipeline complete and verify whether the new fallback prepass behavior improves promotion yield.

## Notes to Carry Forward

- The hardware bottleneck is mostly I/O, not RAM.
- `nproc` should remain the default worker source.
- Cleanup should remain report-first and provenance-preserving.
- Promotion should remain the final step after audit and Pass 1.

