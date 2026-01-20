# Logical Storage Model — Cirrus

## Design Principles
- Storage is named by **role**, not by device.
- Every volume has a single, well-defined purpose.
- Mountpoints are explicit and documented.
- Recovery considerations are addressed before data is placed.

---

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

---

## Future Volumes

Additional volumes will follow the same pattern:
- Named
- Purpose-specific
- Documented before use

Ad-hoc mounts are prohibited.
