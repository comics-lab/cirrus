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
- Fresh snapshot before reset: state-of-hardware-20260315-220018.txt
- Phoenix was then wiped and recreated as a clean Btrfs filesystem
- Phoenix label: `phoenix`
- Phoenix UUID: `16dcd3d6-bfaf-4551-9c3d-ea23ecdf3481`
- Phoenix mountpoint: `/mnt/phoenix`
- Phoenix mount options now include `noatime,compress=zstd:3`
- Phoenix currently mounts the filesystem root (`subvol=/`)
- Implemented subvolumes:
  - `media`
  - `media/comics`
  - `media/books`
  - `media/books/ebooks`
  - `media/books/other`
  - `media/incoming`
  - `services`
  - `services/kavita`
  - `services/mylar`
  - `backups`
  - `staging`

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
Phoenix is now suitable as the long-term data volume for CBR, CBZ, PDF, and other library or service data.

Recommended next step:
- define ownership and write permissions for the created subvolumes
- decide whether Docker should use a Phoenix path directly or a dedicated subvolume
- keep backups and media separated from service state as currently laid out

### Candidate Subvolume Layouts

Full layout:

```text
/mnt/phoenix
├── media
│   ├── comics
│   ├── books
│   └── incoming
├── services
│   ├── kavita
│   ├── mylar
│   └── shared
├── backups
├── staging
└── snapshots
```

Lean layout:

```text
/mnt/phoenix
├── media
│   ├── comics
│   ├── books
│   │   ├── ebooks
│   │   └── other
│   └── incoming
├── services
│   ├── kavita
│   └── mylar
├── backups
└── staging
```

### Selected Baseline

Use the lean layout first.

Status:
- implemented on Phoenix as Btrfs subvolumes on `2026-03-15`

Reason:
- it matches the current known services
- it keeps only one planned expansion under `books`, where format separation is already justified
- it still leaves room to add `shared` or `snapshots` later when there is actual need

Books subtree rationale:
- `ebooks` gives a clean home for EPUB, MOBI, AZW, and similar formats
- `other` provides a deliberate bucket for PDFs or book-adjacent formats that do not behave like standard ebook files
- this avoids having to reorganize a flat `books` directory later

---

## Future Volumes

Additional volumes will follow the same pattern:
- Named
- Purpose-specific
- Documented before use

Ad-hoc mounts are prohibited.
