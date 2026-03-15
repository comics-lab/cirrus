# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-03-15)
- March docs are the current source of truth for repo scope and navigation.
- This repo is host-scoped for Cirrus, not an org-level comics-lab policy repo.
- Root docs were reindexed so `README.md`, `CURRENT_STATE.md`, `SETUP_PLAN.md`, and this file agree on repo purpose and location.
- Hardening baseline already in place: SSH key-only, UFW active, unattended-upgrades enabled, journald persistent, logrotate.timer enabled.
- Phoenix has been recreated as a clean Btrfs volume at `/mnt/phoenix` and now needs a deliberate directory/subvolume layout.
- Docker is not installed on Cirrus.

## Start With
- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `NEXT_STEPS_2026-03-15.md`
- `state-of-hardware-20260315-220018.txt`
- `state-of-hardware-20260126-055629.txt`

## Important References
- `hardening.md`
- `logical_storage.md`
- `cirrus_checklist.md`
- `REPLY_beast-storage-plan_20260125-2147.txt`
- `the_lab/comics-lab-book/01-physical/hardware-inventory.md`
- `the_lab/comics-lab-book/01-physical/storage-physical.md`
- `the_lab/comics-lab-book/01-physical/network-physical.md`
- `the_lab/comics-lab-book/01-physical/overview.md`

## Next Recommended Work
1. Review the `docs-normalization` branch diff before merging it into `main`.
2. Review `SERVICES.md` and apply the recommended keep/drop service baseline.
3. Decide explicitly whether Cirrus is a server with temporary GNOME, or a workstation with services.
4. Define the Phoenix directory or subvolume layout and target ownership model.
5. Capture another state snapshot after any hardening or storage-layout changes.
6. Install Docker only after the storage and hardening decisions are settled.

## Open Questions
- Should Phoenix be wiped and rebuilt now, or kept intact until more data is inspected?
- Which desktop-oriented services are still intentionally enabled on Cirrus?
