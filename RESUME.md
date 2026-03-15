# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-03-15)
- March docs are the current source of truth for repo scope and navigation.
- This repo is host-scoped for Cirrus, not an org-level comics-lab policy repo.
- Root docs were reindexed so `README.md`, `CURRENT_STATE.md`, `SETUP_PLAN.md`, and this file agree on repo purpose and location.
- Hardening baseline already in place: SSH key-only, UFW active, unattended-upgrades enabled, journald persistent, logrotate.timer enabled.
- Phoenix is mounted at `/mnt/phoenix` and still needs an explicit role decision before Docker or service deployment.
- Docker is not installed on Cirrus.

## Start With
- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `NEXT_STEPS_2026-03-15.md`
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
2. Review enabled services and decide Cirrus host identity: server with temporary GNOME, or workstation with services.
3. Resolve Phoenix as staging-only vs durable service data, then document the directory and ownership model.
4. Capture a fresh post-cleanup state snapshot after any hardening or service changes.
5. Install Docker only after the storage and hardening decisions are settled.

## Open Questions
- Should Phoenix be wiped and rebuilt now, or kept intact until more data is inspected?
- Which desktop-oriented services are still intentionally enabled on Cirrus?
