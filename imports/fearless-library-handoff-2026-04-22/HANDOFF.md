# HANDOFF — Fearless Library

## Current State

- Work has shifted from the Cirrus repo session back to direct library work in `/mnt/fearless/LIBRARY`.
- The library root is available and readable.
- Existing local note/artifact paths already present:
  - `FOUND_FILES/`
  - `MISSING_ISSUES.md`

## What Changed Before This Handoff

- `reality.local` NFS and bind-mount state was repaired enough for Cirrus verification.
- The direct `fearless` export is working again.
- The separate `/export/fearless` path is still the broken optional path and should not be used as the basis for library work.
- This handoff set was created so Codex can restart directly in this library root.

## Start-Of-Session Checks

1. Run `pwd` and confirm the session is in `/mnt/fearless/LIBRARY`.
2. Run `ls -la`.
3. Read `AGENTS.md`, `README.md`, `HANDOFF.md`, `MEMORY.md`.
4. Read `MISSING_ISSUES.md`.
5. If current work touches missing-issue recovery or staged matches, then read:
   - `FOUND_FILES/AGENTS.md`
   - `FOUND_FILES/README.md`
   - `FOUND_FILES/HANDOFF.md`
   - `FOUND_FILES/DIALOG.md`
6. Inspect `FOUND_FILES/` if current work relates to missing or recovered issues.

## Recommended Next Work

1. Rebuild local context from the actual publisher directories.
2. Compare current library contents against `MISSING_ISSUES.md`.
3. Decide whether the next task is:
   - issue-gap verification
   - found-file reconciliation
   - publisher-specific cleanup
4. Record any new working assumptions in `MEMORY.md` if they are stable enough to matter next session.

## Latest Operational Note

- On `2026-04-22`, the current missing-issue intake files were staged in `FOUND_FILES/`, verified for embedded `ComicInfo.xml`/`CVDB`, and copied into the live Archie library folders on `cirrus`.
- Mylar follow-through did not complete in the same pass because the configured Mylar service endpoint on port `8690` was unreachable and the local `library.pid` did not correspond to a running process.
- Before updating `MISSING_ISSUES.md`, the next session should start or restore Mylar, run `recheckFiles` and `manualRename` for ComicIDs `9628` and `19398`, then verify the resulting `Have / Total` values.

## Do Not Forget

- Work from the live tree, not from stale repo assumptions.
- Do not use `/export/fearless` as a reference path.
- If mounts look wrong, verify the mount first before touching library content.
- Treat `FOUND_FILES/` as a narrower sub-workflow inside this library root, not as a replacement for the root handoff files.
