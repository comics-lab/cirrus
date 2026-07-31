# Transfer Load Instructions

Use this repo as the startup context for the next session.

## Load Order

1. Read `README.md`
2. Read `AGENTS.md`
3. Read `docs/agent-skill-contract-inventory.md`
4. Read `docs/Agent_Registry.md` and `docs/Director_Routing_Matrix.md`
5. Read the contract and skill matching the requested work
6. Read `RESUME.md`
7. Read `docs/pipeline-v2-notes.md` when intake work is requested
8. Read `docs/intake-to-mylar-workflow.md` for Mylar operations
9. Read `scripts/refresh_intake_pipeline.sh` and `utilities/intake_pipeline.py` for pipeline work

## Current Working State

- Post-conversion intake is now being consolidated into a single Python orchestrator.
- Cleanup is report-driven and replay-based.
- `prepass_normalize.py` now has a fallback metadata path for non-ComicVine identifiers.
- `pass1_batch.sh` and `pass1_then_promote.sh` now default to the live `.cbz` count.
- `file_cleanup_parallel.sh` defaults to `nproc`.
- A Cirrus-local agent registry, routing matrix, contracts, and library-ingest skill now define
  bounded AI assistance roles.
- `docs/transmission-install.md` defines a deferred Docker Transmission deployment for weekly
  comic packs, using NVMe RAID1 for incomplete downloads and Phoenix for completed packs.
- The NVMe pair is `mdadm` RAID1 with Btrfs on `/dev/md0p1`; Phoenix is a separate Btrfs volume.
- The 16 GiB Btrfs swapfile is active and configured through `/etc/fstab`.

## Resume Point (2026-07-31)

- The agentic documentation layer is now defined and linked into repository and wiki navigation.
- The next implementation task is to make the comic metadata resolution/materialization boundary
  use a saved JSON plan so retries do not repeatedly reread or rewrite archives.
- Transmission is documented but not installed; do not deploy it until paths, UID/GID, bandwidth
  limits, and weekly-only torrent handling are reviewed.

## Notes to Carry Forward

- The hardware bottleneck is mostly I/O, not RAM.
- `nproc` should remain the default worker source.
- Cleanup should remain report-first and provenance-preserving.
- Promotion should remain the final step after audit and Pass 1.
- `kavita_ready` and `mylar_ready` are separate states; missing ComicVine ids do not automatically
  make a readable hardcover, trade, or ISBN-only edition invalid for Kavita.
- Local GCD, sidecars, CBL, ISBN, and Metron data should be used before ComicVine API requests.
- Remote ComicVine requests remain sequential, cached, and rate-limited.
- Generated reports, local databases, logs, and Python bytecode should not be committed unless
  explicitly requested.
