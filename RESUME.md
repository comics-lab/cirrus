# Resume — Cirrus

Start in: `/home/rmleonard/Projects/cirrus`

## Current Context (2026-03-27)
- March docs are the current source of truth for repo scope and navigation.
- This repo is host-scoped for Cirrus, not an org-level comics-lab policy repo.
- Root docs were reindexed so `README.md`, `CURRENT_STATE.md`, `SETUP_PLAN.md`, and this file agree on repo purpose and location.
- Hardening baseline already in place: SSH key-only, UFW active, unattended-upgrades enabled, journald persistent, logrotate.timer enabled.
- SMART monitoring is installed and explicitly configured for Phoenix and both NVMe devices.
- Phoenix has been recreated as a clean Btrfs volume at `/mnt/phoenix` and the selected lean subvolume layout has been created.
- Lean Phoenix subvolume layout is the selected baseline; see `logical_storage.md`.
- Phoenix ownership and shared-group policy are documented in `logical_storage.md`.
- Phoenix shared group and ACL baseline have been applied on the live host.
- Two external NFS workflow mounts from `reality.local` are now in place:
  - `/mnt/old_library`
  - `/mnt/incoming-root`
- Docker is now installed and the daemon baseline is active.
- JDownloader 2 is now deployed as the first application container, with no browser UI port published.
- Canonical source-class paths now exist under Phoenix:
  - `/mnt/phoenix/media/sources/legacy_mylar`
  - `/mnt/phoenix/media/sources/upstream_incoming`
- Reference service/proxy configs from `reality.local` are staged under:
  - `/mnt/incoming-root/reality-config-export/`
- JDownloader 2 is now the first planned application candidate, but it has not been deployed yet.
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

Latest remote-access result:
- FileBrowser Pro SFTP access to Cirrus works with a dedicated imported SSH key
- temporary password auth was enabled only long enough to retrieve the key file, then removed
- Cirrus is back to key-only SSH

Latest Docker result:
- Docker Engine, containerd, buildx, and compose plugin are installed from Docker's official Debian repo
- `/etc/docker/daemon.json` is in place with `log-driver=local` and `live-restore=true`
- Docker is enabled and active
- JDownloader 2 is deployed from `/srv/compose/jdownloader2/docker-compose.yml`
- no browser UI port is published for JDownloader
- next validation is MyJDownloader pairing and a test download

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?

## Next Recommended Work
1. Pair the running JDownloader container with MyJDownloader.
2. Perform a small test download and verify that files land in `/mnt/phoenix/media/incoming/jdownloader`.
3. Confirm resulting ownership and permissions still match the shared `media`-group policy.
4. Pause again before introducing any second application.

Separate note cleared:
- `reality.local` is back online, so the temporary `fearless` recovery incident is no longer part of the active Cirrus handoff.
