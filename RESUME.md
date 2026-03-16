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
- Suspend is hard-disabled system-wide and GNOME idle suspend is disabled for both `rmleonard` and `Debian-gdm`

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
1. Reboot and leave the box idle for about one hour with no keyboard interaction.
2. Confirm the host still appears up, then test remote login first and local login second.
3. Verify Bluetooth connectivity after the reboot test.
4. If the host remains stable, proceed to Docker installation from the documented baseline.

## Reboot Watch

After the next reboot, check these first:
- whether `/mnt/phoenix` is mounted automatically before any manual `mount -a`
- whether the current boot journal shows `mnt-phoenix.mount` mounting and staying mounted
- whether `plymouth-quit-wait.service` or graphical startup stalls boot again
- whether wired and Wi-Fi both come up normally, and when
- whether the host stays up for about one hour with no local input and does not auto-suspend
- whether remote login works before local login
- whether `cirrus.local` still resolves to the wired address
- whether Bluetooth still works after the idle-period reboot test

Known prior behavior from the last boot:
- Phoenix did mount successfully during boot
- Phoenix was later unmounted during the same boot session
- `plymouth-quit-wait.service` held the boot path for about 15 minutes

Latest reboot result:
- Phoenix auto-mounted successfully
- network came up normally
- Codex resolved cleanly from the standardized `nvm` path

Latest suspend finding:
- suspend from the greeter caused `mnt-phoenix.mount` to be unmounted on resume
- Phoenix had to be remounted manually
- suspend is now hard-disabled until the host proves stable across long idle periods

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?
