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

Important scale note:
- the intended comics library is expected to span roughly 20TB or more across the full collection
- the current Phoenix disk is not the final capacity solution for that full corpus
- the current Phoenix layout should therefore be treated as the policy baseline for path roles, permissions, and service behavior, not proof that final storage capacity is already solved
- avoid any path scheme that would require a major reorganization when larger or additional storage is introduced later

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

### Ownership Map

Recommended shared group:
- group name: `media`
- human operator: `rmleonard` should be a member
- container group: both Kavita and Mylar should run with this shared `PGID`

Recommended policy:
- use one shared group for manual operations and service access
- keep one primary writer per library tree wherever possible
- keep service config/state separated from library content
- use setgid directories and default ACLs on shared writable trees

Subvolume ownership map:

| Path | Intended owner | Group | Mode | Primary writer | Notes |
|---|---|---|---|---|---|
| `/mnt/phoenix/media` | `root` | `media` | `2775` | human/admin | top-level container for library trees |
| `/mnt/phoenix/media/comics` | `root` | `media` | `2775` | Mylar | Kavita should mount read-only if possible |
| `/mnt/phoenix/media/books` | `root` | `media` | `2775` | human/admin | top-level subtree for non-comics books |
| `/mnt/phoenix/media/books/ebooks` | `root` | `media` | `2775` | human/admin | EPUB, MOBI, AZW, similar |
| `/mnt/phoenix/media/books/other` | `root` | `media` | `2775` | human/admin | PDFs and non-standard book formats |
| `/mnt/phoenix/media/incoming` | `root` | `media` | `2775` | human/admin and Mylar if needed | staging/quarantine before final placement |
| `/mnt/phoenix/services` | `root` | `media` | `2775` | human/admin | top-level container for service state |
| `/mnt/phoenix/services/kavita` | service UID or `root` | `media` | `2775` | Kavita | writable app state/config/cache |
| `/mnt/phoenix/services/mylar` | service UID or `root` | `media` | `2775` | Mylar | writable app state/config/cache |
| `/mnt/phoenix/backups` | `root` | `media` | `2775` | human/admin | exported backups only, not live app state |
| `/mnt/phoenix/staging` | `root` | `media` | `2775` | human/admin | bulk repair, reorg, and temporary work |

File mode target:
- regular files on shared trees: `0664`

Directory mode target:
- shared directories: `2775`

ACL baseline:
- set default ACLs so new files and directories inherit group `media` write access on:
  - `/mnt/phoenix/media`
  - `/mnt/phoenix/services`
  - `/mnt/phoenix/backups`
  - `/mnt/phoenix/staging`

Container mapping recommendation:
- Kavita and Mylar should use the same `PGID`
- Mylar should be the primary writer for `/mnt/phoenix/media/comics`
- Kavita should prefer read-only access to library trees and write only within `/mnt/phoenix/services/kavita`
- human/manual operations should be performed by `rmleonard` through the shared `media` group, not by loosening permissions to world-writable

### Multi-Application Library Policy

The current layout should now be interpreted as a multi-application library model, not a simple two-app arrangement.

Expected actor classes:
- acquisition applications
- organizer or post-processor applications
- library or reader applications
- human administrative access
- backup or export workflows

Default role policy:
- acquisition applications write into `media/incoming` and nowhere else by default
- organizer applications may read `media/incoming` and write into curated library trees only if explicitly designated as the primary writer for that tree
- reader and display applications should read curated library trees and write only within their own `services/<app>` state paths
- human administrative access may operate across the library through the shared `media` group, but should prefer deliberate repair, ingest, and reorganization work in `incoming` or `staging`
- backups and exports should read from curated trees and write only into `backups`

Curated tree policy:
- `media/comics` is a curated library tree
- `media/books/ebooks` is a curated library tree
- `media/books/other` is a curated library tree
- each curated tree should have one primary writer at a time
- additional applications should be treated as readers unless a specific multi-writer need is documented

Current designated-writer baseline:
- `media/comics`: primary writer is the organizer or acquisition stack represented today by Mylar
- `media/books/ebooks`: primary writer is human or admin workflow until a specific organizer is adopted
- `media/books/other`: primary writer is human or admin workflow until a specific organizer is adopted
- `media/incoming`: shared writable intake area for acquisition and manual ingest
- `staging`: shared repair or reorganization area, not the long-term library

Collision-avoidance rule:
- do not let multiple applications rename or reorganize the same curated library tree by default
- if a second writer is ever allowed, document the exact reason and the expected boundary between the writers first

Planned path expansion:
- if multiple acquisition pipelines are introduced, expand under `media/incoming` first rather than fragmenting the curated library layout
- if multiple organizer workflows are introduced, prefer separate `staging` or service-state paths rather than giving all organizers broad write access to curated trees
- if a future larger storage target replaces or augments Phoenix, preserve these same role-based paths so the application layer does not need a wholesale remap

### Administrative Remote Access Policy

Preferred protocol:
- `SFTP` via the existing OpenSSH service

Reason:
- it reuses the current SSH hardening baseline
- it respects existing UNIX ownership, groups, and ACLs on Phoenix
- it avoids introducing a second network file service before Docker and application layout are finished

Operational guidance:
- administrative remote access should use the real user account and SSH keys
- remote manual changes should occur through the shared `media` group model already documented here
- avoid protocol-specific alternate permission models unless there is a clear interoperability need

If a later `SMB` share is added for convenience:
- export only deliberate library or staging paths
- do not export broad roots casually
- keep share layout aligned with the documented Phoenix subvolume roles
- treat SMB as an additional access layer, not the primary source of truth for permissions

### Applied Baseline (2026-03-15)

The following have been applied on the live host:
- group `media` created
- user `rmleonard` added to group `media`
- `/mnt/phoenix/media`, `/mnt/phoenix/services`, `/mnt/phoenix/backups`, and `/mnt/phoenix/staging` set to group `media`
- shared directories set to mode `2775`
- default ACLs added so group `media` inherits `rwx` on new files and directories under the shared trees

---

## Future Volumes

Additional volumes will follow the same pattern:
- Named
- Purpose-specific
- Documented before use

Ad-hoc mounts are prohibited.
