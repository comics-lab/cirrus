
# Restart Work Now — Cirrus Setup

_Last checkpoint: 2026-01-19_

## Context Snapshot
Work resumed on **Cirrus** after stabilizing The Beast and documenting storage truth.

Key actions already completed:
- Canonical storage inventory for **The Beast** created (Btrfs + ext4, Fearless degraded).
- Cirrus local notes (`cirrus-notes.tar.gz`) uploaded and fully reviewed:
  - architecture.md
  - allocation.txt
  - hardening.md
  - unit-files-enabled.txt
  - world-writeable-dirs.txt
  - BASH_History.log
- Conclusion: Cirrus was *paused*, not abandoned; design aligns with current goals.

## Agreed Architectural Decisions
- **Boot Volume**  
  - Abstract concept (NVMe RAID1 implementation details hidden in appendices).
- **Phoenix**  
  - First named non-boot data volume.
  - Holds persistent application data and media.
- Device-level details are excluded from main architecture docs.

## Host Roles (Confirmed)
- **Cirrus**: Primary production host (Mylar, Kavita via Docker).
- **Hippy**: Ingress / acquisition (JDownloader), isolated.
- **Zima**: Prototyping / testing.
- **The Beast & Dudley**: Development, design, analysis.
- **Hawkeye**: Network services / monitoring.

## Documentation Tracks In Progress
Three tracks agreed to begin in parallel:

1. **architecture.md**
   - Update (append, not rewrite) to reflect:
     - Cirrus as primary services host
     - Phoenix volume
     - Revised host role boundaries

2. **logical_storage.md** (Cirrus-specific)
   - Define:
     - Boot Volume
     - Phoenix
     - Rules for future named volumes

3. **build-log.md**
   - Chronological, append-only
   - Records what is actually done (OS, hardening, packages, storage steps)

## npm / Node Decision
- npm will be provided via Debian packages:
  ```bash
  sudo apt update
  sudo apt install -y nodejs npm
