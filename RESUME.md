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
- JDownloader 2 is now the first working application container on Cirrus, with MyJDownloader functioning and LAN-only browser UI on `192.168.1.113:5800`.
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
- LAN-only browser UI remains available for JDownloader at `192.168.1.113:5800`
- JDownloader baseline is validated; next work is defining the post-download processing boundary
- Imported a curated subset of Mylar post-download utility docs/scripts into `imports/mylar-utilities-post-download/`; next session should examine and adapt them to the current Cirrus intake model.
- A new Cirrus-native `utilities/cbr_to_cbz.py` now exists and has passed a dry-run against `/mnt/phoenix/media/incoming/jdownloader`; next step is a controlled real conversion batch before building the metadata audit utility.
- `utilities/cbr_to_cbz.py` has now completed a live test batch: one `.cbr` converted cleanly, and two archives were left untouched with likely-corrupt extraction failures recorded in the CSV report.
- `utilities/cbz_audit.py` now exists and has completed a first live audit pass against intake `.cbz` files, confirming that root `ComicInfo.xml` is present on some files but ComicVine references are still inconsistent.
- `utilities/cbz_audit.py` now matches upstream Mylar's actual import baseline more closely: a file is only treated as `mylar_import_valid` if root `ComicInfo.xml` parses, `Series` and `Number` are present, and a ComicVine issue reference is recoverable from `Notes` or `Web`.
- The local GCD database remains useful for descriptive issue metadata, but it does not contain direct ComicVine issue IDs or ComicVine URLs in `gcd_issue` or `gcd_series`.
- The old `metroninfo_fill.py` helper cannot run on Cirrus as written because the expected local `METRON/darkseid` code tree is not present here; any new Metron stage will need a fresh, Cirrus-native dependency plan.

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?

## Next Recommended Work
1. Extend the post-download routing logic around the stricter `mylar_import_valid` baseline from `utilities/cbz_audit.py`.
2. Decide the exact alternate-processing path for archives that are readable but not yet Mylar-valid.
3. Build the next Cirrus-native metadata utility around real available sources: GCD for descriptive metadata and ComicVine-aware tooling for issue IDs.
4. Do not introduce a second application container until the intake-routing rules are explicit and tested.

Separate note cleared:
- `reality.local` is back online, so the temporary `fearless` recovery incident is no longer part of the active Cirrus handoff.
