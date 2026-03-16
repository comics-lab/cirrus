# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-03-15)
- March docs are the current source of truth for repo scope and navigation.
- This repo is host-scoped for Cirrus, not an org-level comics-lab policy repo.
- Root docs were reindexed so `README.md`, `CURRENT_STATE.md`, `SETUP_PLAN.md`, and this file agree on repo purpose and location.
- Hardening baseline already in place: SSH key-only, UFW active, unattended-upgrades enabled, journald persistent, logrotate.timer enabled.
- SMART monitoring is installed and explicitly configured for Phoenix and both NVMe devices.
- Phoenix has been recreated as a clean Btrfs volume at `/mnt/phoenix` and the selected lean subvolume layout has been created.
- Docker is not installed on Cirrus.
- Lean Phoenix subvolume layout is the selected baseline; see `logical_storage.md`.
- Phoenix ownership and shared-group policy are documented in `logical_storage.md`.
- Phoenix shared group and ACL baseline have been applied on the live host.
- Codex CLI path was standardized after a split-install issue; `codex` now resolves from `~/.nvm/versions/node/v25.8.0/bin/codex` and reports `codex-cli 0.114.0`
- Avahi is restricted to the wired interface so `cirrus.local` resolves to `192.168.1.113`

## Start With
- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `NEXT_STEPS_2026-03-15.md`
- `state-of-hardware-20260315-230117.txt`
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
1. Review `SERVICES.md` and continue the minimal-desktop service baseline cleanup.
2. Remove only the explicitly unwanted CUPS services first.
3. Begin Docker installation planning from the documented Docker baseline.
4. Install Docker only after the storage and hardening decisions are settled.

## Reboot Watch

After the next reboot, check these first:
- whether `/mnt/phoenix` is mounted automatically before any manual `mount -a`
- whether the current boot journal shows `mnt-phoenix.mount` mounting and staying mounted
- whether `plymouth-quit-wait.service` or graphical startup stalls boot again
- whether wired and Wi-Fi both come up normally, and when

Known prior behavior from the last boot:
- Phoenix did mount successfully during boot
- Phoenix was later unmounted during the same boot session
- `plymouth-quit-wait.service` held the boot path for about 15 minutes

Latest reboot result:
- Phoenix auto-mounted successfully
- network came up normally
- Codex resolved cleanly from the standardized `nvm` path

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?
