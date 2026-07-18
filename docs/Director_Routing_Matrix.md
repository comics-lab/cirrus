# Cirrus Routing Matrix

Use this matrix to select the smallest role that can safely perform a request.

| Intent or keywords | Primary role | Required skill | Required validation |
| --- | --- | --- | --- |
| host truth, mounts, disks, system state | Cirrus Host Agent | `host-truth-capture` | Compare live state with current docs |
| Btrfs, storage, permissions, library placement | Cirrus Host Agent | `host-storage-baseline` or `shared-library-storage` | Verify mounts, ownership, and rollback |
| SSH, firewall, SMART, hardening | Cirrus Host Agent | `host-hardening-baseline` | Verify live hardening state |
| Docker service baseline or service inventory | Cirrus Host Agent | `service-baseline-review` | Check active/enabled services |
| restart, handoff, resume, park | Cirrus Host Agent | `host-resume-handoff` | Update resume and action log |
| CBZ, ComicInfo, MetronInfo, ComicVine, GCD, ISBN, CBL | Comic Metadata Intake Agent | `comic-metadata-intake` | Validate archive, XML, provenance, and disposition |
| library discovery, catalog, source inventory, collection layout | Library Ingest Agent | `library-ingest` | Integrity report and rollback plan |
| promote, Mylar import, recheck, metatag, Kavita scan | Mylar Handoff Agent | `comic-metadata-intake` | Confirm `mylar_ready`, destination safety, and post-import state |
| scheduled scan, queue monitoring, API retry, alerting | Host Agent plus explicit monitor design | None currently | Define idempotency, rate limits, and rollback first |

## Ambiguity Rules

- Prefer the comic specialist for archive and metadata work, even when the destination is a host service.
- Prefer the host role for mounts, containers, permissions, and service availability.
- Keep GCD/CBL/ComicVine corrections in review until explicitly approved.
- If a request mutates files or publishes changes, require a dry-run or saved plan first.
- If multiple roles match, select one primary owner and record the boundary between roles.
