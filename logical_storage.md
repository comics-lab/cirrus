# Logical Storage Model — Cirrus

## Design Principles
- Storage is named by **role**, not by device.
- Every volume has a single, well-defined purpose.
- Mountpoints are explicit and documented.
- Recovery considerations are addressed before data is placed.

---

## Current Implementation (2026-01-25)
- Boot volume: Btrfs on md0p1 (NVMe RAID), subvols / and /home
- Phoenix: /mnt/phoenix on /dev/sda1 (Btrfs), mounted via fstab
- Phoenix mount options: rw,relatime,space_cache=v2,subvolid=5,subvol=/
- Phoenix usage: 3.7T total, 3.1T used (84%)
- State log: state-of-hardware-20260126-055629.txt

## Live Verification (2026-03-15)
- Fresh snapshot: state-of-hardware-20260315-220018.txt
- Phoenix is still mounted directly at `/mnt/phoenix`
- Phoenix still uses the filesystem root (`subvol=/`), not a service-specific subvolume layout
- Top-level directories include `bin`, `boot`, `dev`, `etc`, `home.old`, `root`, `usr`, and `var`
- That layout strongly indicates Phoenix is carrying an old system image or recovery payload rather than a deliberate application-data structure

## Boot Volume

### Purpose
The Boot Volume contains:
- Operating system
- System configuration
- Container runtime binaries and metadata

### Characteristics
- Fast
- Redundant
- Minimal in scope

### Non-Goals
The Boot Volume does NOT contain:
- Media libraries
- Bulk datasets
- Long-term application content

Implementation details are intentionally abstracted.

---

## Phoenix (Primary Data Volume)

Phoenix is the **first named non-boot volume** on Cirrus.

### Purpose
Phoenix holds:
- Persistent container data
- Media libraries
- Application state that must survive rebuilds of the Boot Volume

### Characteristics
- Durable
- Explicitly mounted
- Backed up independently of the Boot Volume
- Ownership and permissions managed deliberately

### Relationship to Services
All production containers on Cirrus bind-mount or store volumes on Phoenix
unless explicitly documented otherwise.

### Current Recommendation
Do not use Phoenix for Docker `data-root` or production bind mounts yet.

First:
- review and preserve any legacy data that matters
- decide whether Phoenix will be wiped and rebuilt
- create an explicit directory or subvolume layout for service data
- then treat it as the durable data volume

---

## Future Volumes

Additional volumes will follow the same pattern:
- Named
- Purpose-specific
- Documented before use

Ad-hoc mounts are prohibited.
