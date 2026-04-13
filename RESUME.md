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
- `utilities/cv_issue_resolver.py` now exists as the pre-ComicTagger lookup stage: it uses existing root metadata plus filename/path inference to query ComicVine and emit a CSV report, with conservative `resolved`, `candidate`, and `unresolved` buckets instead of blindly auto-tagging weak matches.
- A direct proof run against upstream ComicTagger 1.6.0-beta.10 confirmed that a known ComicVine issue ID can be written into a `.cbz` as a root `ComicInfo.xml` that passes the stricter `cbz_audit.py` / Mylar-valid checks.
- Intake work is no longer limited to `media/incoming/jdownloader`; adjacent directories under `media/incoming`, currently `comics-local` and `weekly-lots`, may also be sampled for conversion, audit, and tagging work, but anything explicitly labeled `WebP` should be excluded from automated processing.
- `/mnt/phoenix/media/incoming/mylar-import` now exists as the dedicated Pass 1 output and Mylar handoff directory; Mylar should only be API-triggered after Pass 1 finishes and moves ready archives there.
- `utilities/pass1_write_comicinfo.py` now exists as the first Pass 1 wrapper, but the current JDownloader intake set has no safe new auto-writes yet: one file was already Mylar-valid and has been promoted separately, three files remain `candidate`, and one remains `unresolved`.
- `utilities/promote_mylar_import.py` successfully moved the already-valid Batman omnibus from raw JDownloader intake into `/mnt/phoenix/media/incoming/mylar-import`.
- `/mnt/phoenix/media/incoming/metadata-review` is now the defined alternate-processing path for resolver `candidate` and `unresolved` files.
- Current policy choice: `candidate` and `unresolved` files are a manual move into `metadata-review`; they should be fixed there manually, rescanned, and only then promoted into `mylar-import` if they pass `mylar_import_valid`.
- `utilities/verify_weekly_pack_extracts.py` now exists and has verified which weekly-pack trees are trustworthy as a broader non-`WebP` test corpus:
  - `weekly-lots/2026.03.25` is fully verified
  - `reality_weekly-lots/2026.02.25` is fully verified
  - `reality_weekly-lots/2026.02.11` is partially verified (Image and Marvel only)
  - newer `reality_weekly-lots` packs for `2026.03.04`, `2026.03.11`, and `2026.03.18` still have zip files but no extracted publisher directories
- Important next resolver fix: `Detective Comics 1107 (2026)` in the verified `2026.03.25` weekly pack is currently marked `unresolved`, but direct ComicVine issue search shows a valid match (`issue_id=1160271`) under volume `91098` (`Detective Comics`, 2016). The unresolved result is therefore a resolver logic gap caused by over-preferring the legacy `1937` volume (`18058`) for long-running series names.
- JDownloader integrity follow-up remains partially open: current evidence suggests the remaining JDownloader `.cbr` files are largely readable and that some earlier failures were extractor-specific rather than true archive damage, but `utilities/cbr_to_cbz.py` still needs a clean full rerun with the new `7z` fallback before any archive is formally sidelined for re-download.
- The local GCD database remains useful for descriptive issue metadata, but it does not contain direct ComicVine issue IDs or ComicVine URLs in `gcd_issue` or `gcd_series`.
- The old `metroninfo_fill.py` helper cannot run on Cirrus as written because the expected local `METRON/darkseid` code tree is not present here; any new Metron stage will need a fresh, Cirrus-native dependency plan.
- The preferred raw-archive recovery method on Cirrus is now:
  1. rename `.cbr` to `.rar`
  2. verify with `file` that the archive is actually `RAR archive data`
  3. extract with `unrar`
  4. rebuild normalized `.cbz`
  5. move rebuilt `.cbz` into `metadata-review/quarantine-normalized`
  6. archive the raw `.rar` originals
- Raw archive quarantine is effectively cleared as active work; the previously active `2026-04-11-jdownloader` and `2026-04-13-jdownloader` batches were rebuilt and moved into `metadata-review/quarantine-normalized`, and the stale `2026-04-10-prior-downloads` raw originals were archived because matching `.cbz` files already existed downstream.
- A fresh full JDownloader audit/resolver cycle was completed before the latest manual ComicTagger wave:
  - full audit snapshot: `157` `.cbz`, `30` root `ComicInfo.xml`, `3` already-`mylar_valid`
  - full resolver snapshot: `6` resolved, `120` candidates, `31` unresolved
- The repaired ComicTagger environment is now `/tmp/comictagger-pass1d`; the older `/tmp/comictagger-pass1b` wrapper is broken and should not be reused.
- The five remaining high-confidence resolved JDownloader files were successfully tagged with the repaired ComicTagger environment and promoted into `/mnt/phoenix/media/incoming/mylar-import`.
- Neither normalized quarantine batch contains any further safe automatic Pass 1 wins:
  - `2026-04-11-jdownloader`: `0` resolved, `2` candidates, `11` unresolved
  - `2026-04-13-jdownloader`: `0` resolved, `0` candidates, `6` unresolved
- Blind medium-confidence auto-writing is not productive enough to continue: a bounded nine-file test failed to produce any new `mylar_valid` files.
- After a manual ComicTagger session on Cirrus, the live JDownloader audit changed substantially:
  - `149` `.cbz` in scope before promotion
  - `99` files with root `ComicInfo.xml`
  - `77` files with ComicVine refs
  - `77` files `mylar_valid`
- Those `77` valid files were promoted into `/mnt/phoenix/media/incoming/mylar-import`.
- Current live intake after that promotion:
  - JDownloader intake: `72` `.cbz`
  - Mylar staging: `100` `.cbz` in `/mnt/phoenix/media/incoming/mylar-import`
  - remaining JDownloader set: `72` files, `22` with root `ComicInfo.xml`, `0` ComicVine refs, `0` `mylar_valid`

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?

## Next Recommended Work
1. Install Docker Mylar now. The staging threshold has been crossed decisively: `/mnt/phoenix/media/incoming/mylar-import` now holds `100` `.cbz` files.
2. Bind Mylar only to the intended paths:
   - config/state on Phoenix services storage
   - import input at `/mnt/phoenix/media/incoming/mylar-import`
   - final library output according to the existing Phoenix storage policy
3. Verify the exact Mylar API `forceProcess` call and test import behavior on a small controlled subset before letting it consume the whole staged backlog.
4. Keep the remaining JDownloader set (`72` `.cbz`) in review; do not continue blind medium-confidence auto-writes.
5. Leave normalized quarantine files in `metadata-review/quarantine-normalized` for explicit review rather than automatic promotion; there are no safe automatic wins left there.
6. Continue using the `rename -> verify RAR -> unrar -> rebuild` workflow for any future raw archive recovery on Cirrus.

Separate note cleared:
- `reality.local` is back online, so the temporary `fearless` recovery incident is no longer part of the active Cirrus handoff.
