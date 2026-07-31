# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-07-31)
- The intake pipeline is being consolidated into a single Python orchestrator that starts after `cbr_to_cbz`.
- Cleanup is now report-driven and replay-based.
- `prepass_normalize.py` now has a fallback path for non-ComicVine identifiers, and it can still write both `ComicInfo.xml` and `MetronInfo.xml`.
- `pass1_batch.sh` and `pass1_then_promote.sh` now default to the live `.cbz` count instead of a hardcoded 500.
- `file_cleanup_parallel.sh` now defaults to `nproc`.
- `utilities/intake_pipeline.py` is the current high-level entrypoint for the post-conversion flow.
- `docs/agent-skill-contract-inventory.md` is the current reference for agents, skills, contracts,
  personas, behaviors, and executable assistance boundaries.
- `docs/Agent_Registry.md` and `docs/Director_Routing_Matrix.md` define the current bounded roles.
- `docs/transmission-install.md` is a deferred runbook; Transmission is not installed.
- A 16 GiB Btrfs swapfile on the NVMe RAID1 stack is active and configured at boot.
- The current hardware model to remember:
  - `/dev/md0` is the local NVMe Btrfs array
  - `/dev/sda` is a USB3 volume
  - other `/mnt/*` mounts are NFS
  - zram may be active
  - the host has 16 GiB RAM

## Start With
- `README.md`
- `AGENTS.md`
- `docs/agent-skill-contract-inventory.md`
- `docs/Agent_Registry.md`
- `docs/Director_Routing_Matrix.md`
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
- What JSON schema should carry the approved resolution/materialization plan between parser stages?
- Which local metadata fields should be authoritative for hardcover, trade, omnibus, and ISBN-only editions?
- When Transmission is approved, what UID/GID and bandwidth limits should it share with the media services?

## Next Recommended Work
1. Define and implement the saved JSON resolution/materialization plan for comic intake.
2. Add contract-level validation for provenance, confidence, XML validity, and `mylar_ready` promotion.
3. Keep cleanup replay as the only report-driven apply step.
4. Keep the `nproc` worker default and live `.cbz` count limit behavior.
5. Review the Transmission runbook before any Docker deployment.

## Practical Next Step
1. Load the applicable agent skill and contract before changing host or intake behavior.
2. Keep the Archie plain-series migration lane paused until there is a deliberate batch to process.
3. Keep JDownloader as the active raw intake queue and only promote files into `mylar-import` when they are true standalone candidates for Mylar folder processing.
4. Keep generated reports, databases, logs, and bytecode outside commits unless explicitly requested.
