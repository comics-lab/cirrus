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
  - JDownloader intake: `112` `.cbz`
  - Mylar staging: `100` `.cbz` in `/mnt/phoenix/media/incoming/mylar-import`
  - remaining JDownloader set: `112` files split as `29` medium-confidence candidates, `34` low-confidence candidates, `52` unresolved, and `1` resolver error
- Docker Mylar is now deployed from `/srv/compose/mylar3/docker-compose.yml`:
  - UI: `http://192.168.1.113:8090`
  - config: `/mnt/phoenix/services/mylar`
  - imports: `/mnt/phoenix/media/incoming/mylar-import`
  - library target: `/mnt/phoenix/media/comics`
- Docker Kavita is now deployed from `/srv/compose/kavita/docker-compose.yml`:
  - UI: `http://192.168.1.113:5000`
  - config: `/mnt/phoenix/services/kavita`
  - library source: `/mnt/phoenix/media/comics` mounted read-only
- Current Mylar startup state is healthy apart from the expected missing ComicVine API key warning.
- The current Pass 1 wrapper must prefer `/tmp/comictagger-pass1d/bin/comictagger`; direct ComicTagger writes against that environment succeeded for both the resolved slice and a bounded medium-confidence batch.
- Cross-host search handoff is now established under `/mnt/phoenix/media/incoming/fearless-ssh/LIBRARY`:
  - `MISSING_ISSUES.md` in the library root
  - `FOUND_FILES/README.md`
  - `FOUND_FILES/HANDOFF.md`
  - `FOUND_FILES/AGENTS.md`
  - `FOUND_FILES/DIALOG.md`
- Matching repo-side templates now exist under `templates/reality-library-handoff/` so the external handoff workspace can be recreated or versioned cleanly.
- `utilities/mylar_series_import.py` now exists as the preferred Archie-style bulk migration helper for pre-organized library trees with `series.json`. It adds series by ComicVine volume id, copies issue files into Mylar `ComicLocation`, then runs `recheckFiles` and `manualRename`.
- `utilities/mylar_paced_import.py` also exists, but the older one-file-at-a-time `forceProcess` approach is not the right path for Archie bulk migration.
- The active large-source migration lane is now `/mnt/phoenix/media/incoming/fearless-ssh/LIBRARY/Archie Comics`.
- Audit of the Archie subtree established:
  - `1825` `.cbz`
  - `1825` root `ComicInfo.xml`
  - `1770` recoverable ComicVine refs / `mylar_valid`
  - `55` holdbacks
- The `55` Archie holdbacks are tracked in `/tmp/archie_holdbacks_2026_04_21.csv`; they are mostly plain issues missing ComicVine refs plus a smaller digest/anthology subset, not duplicates or annuals.
- The correct Archie migration path is now proven to be series-aware, not blind staged `forceProcess`.
- Proven-complete Archie plain-series imports currently in Mylar:
  - `Comet (1983)` `2 / 2`
  - `Fly Man (1965)` `8 / 8`
  - `Adventures of the Jaguar (1961)` `15 / 15`
  - `Adventures of the Fly (1960)` `25 / 25`
  - `Archie & Friends (1992)` `159 / 159`
  - `The Black Hood (1983)` `3 / 3`
  - `The Hangman (2015)` `4 / 4`
  - `The Fly (1959)` `6 / 6`
  - `Archie Comics (1942)` `113 / 113`
  - `Archie at Riverdale High (1972)` `113 / 113`
  - `Betty And Veronica: Summer Fun (1994)` `6 / 6`
  - `Archie is Mr. Justice (2025)` `4 / 4`
  - `Hangman Comics (1942)` `7 / 7`
- Two Archie series are now confirmed source-limited rather than importer-broken:
  - `Archie (1960)` `546 / 553`, missing `151, 191, 237, 261, 266, 269, 489`
  - `Black Hood Comics (1943)` `10 / 11`, missing `15`
- Those missing issues are now tracked in repo root `MISSING_ISSUES.md` and mirrored to `/mnt/phoenix/media/incoming/fearless-ssh/LIBRARY/MISSING_ISSUES.md`.

## Open Questions
- Which desktop-oriented services are still intentionally enabled on Cirrus?

## Next Recommended Work
1. Continue the Archie plain-series migration lane with `utilities/mylar_series_import.py`, keeping annuals/digests/special-format directories out of the automated batch.
2. Let the `reality.local` side use `LIBRARY/MISSING_ISSUES.md` plus `FOUND_FILES/` to search for the confirmed Archie source gaps and stage any matches.
3. Keep Pass 1 focused on the live JDownloader queue separately; do not mix bulk Archie migration with weak JDownloader resolver candidates.
4. Revisit the `55` Archie holdbacks later as a smaller metadata-repair batch once the plain-series lane is exhausted.

## Additional Current Work
- `reality.local:/mnt/fearless` is restored on Cirrus and currently mounts cleanly.
- Verified live from Cirrus:
  - `showmount -e 192.168.1.126` advertises both `/mnt/fearless` and `/export/fearless`
  - a fresh mount of `192.168.1.126:/mnt/fearless` shows the expected top-level tree: `A`, `books`, `comics`, `docker`, `Downloads`, `DOWNLOADS`, `From_Longbox`, `LIBRARY`
  - Cirrus now has the intended live mount back at `/mnt/fearless`
- On `reality.local`, the commented bind-mount block in `/etc/fstab` lines `44` through `57` has now been restored:
  - `/mnt/DC`
  - `/mnt/pubs/Comics/Publishers/DC`
  - `/mnt/longbox`
  - `/mnt/shortbox`
  - `/home/Various-Downloads/Various/else-where/FLBM-*`
  - `/mnt/grackle/LIBRARY/{Archie Comics,Dark Horse Comics,Rebellion}`
  - line `57` required a typo fix from `Mylar-Shortbox-ROO` to `Mylar-Shortbox-ROOT`
- The remaining NFS problem is narrower and server-side:
  - `192.168.1.126:/export/fearless` mounts as an empty directory from Cirrus
  - the old stale client test mount to `/mnt/fearless-test` has been removed
  - the direct export path is good; the bind-export path is the broken one
- During verification, `reality.local:/mnt/longbox` briefly failed from Cirrus over NFSv4 with `Stale file handle` even though NFSv3 worked.
- A restart of `nfs-server` on `reality.local` cleared that condition; after restart, Cirrus successfully mounted `/mnt/DC`, `/mnt/shortbox`, `/mnt/longbox`, and `/mnt/fearless` over NFSv4.
- Current conclusion:
  - do not use `/export/fearless` for Cirrus
  - keep Cirrus pointed at `reality.local:/mnt/fearless`
  - the restored bind mounts and direct exports are now usable
  - if the bind-export is still needed on `reality.local`, the next server-side checks are `findmnt /export/fearless`, `ls -la /export/fearless`, `exportfs -v`, and `/proc/fs/nfsd/exports`

Separate note cleared:
- `reality.local` is back online, so the temporary `fearless` recovery incident is no longer part of the active Cirrus handoff.

## New Current Resume Point
- The external `FOUND_FILES` handoff from `fearless-ssh/LIBRARY` has now been imported back into the repo under `imports/fearless-library-handoff-2026-04-22/` and reconciled against live Mylar state.
- The previously missing `Archie (1960)` issues `151, 191, 237, 261, 266, 269, 489` and `Black Hood Comics (1943) #15` were copied from the staged `FOUND_FILES` set into the live Cirrus library, rescanned, renamed, and verified in Mylar as fully downloaded. `MISSING_ISSUES.md` is now empty.
- `utilities/dc_finest_metadata.py` now exists to write ISBN/GCD/Metron-style rooted metadata for `DC Finest` books without using ComicVine IDs. Three `DC Finest` books were enriched with both `ComicInfo.xml` and `MetronInfo.xml` and moved into `/mnt/phoenix/media/comics/DC Comics/DC Finest/` for library use.
- JDownloader was cleaned again and is now back to a structurally sane raw boundary:
  - `98` `.cbz`
  - `0` `.cbr`
  - `0` `.zip`
  - `4` `.pdf`
- `utilities/seed_legacy_series_metadata.py` now exists and is the entry point for seeding JDownloader runs from legacy library sidecars plus the local GCD DB.
- `utilities/cv_issue_resolver.py` has been patched so that if a parent `series.json` contains a trusted ComicVine `comicid`, the resolver uses that series identity first instead of fuzzy re-guessing the volume. It also now normalizes malformed year text into a real 4-digit year.
- That seeded resolver workflow is now proven on JDownloader:
  - `Ultimate Elektra` `5 / 5`
  - `Mantra v1` `24 / 24`
  - `Mantra v2` `7 / 7`
  - `Superboy & The Ravers` `19 / 19`
  - `Marvel Mutts Infinity Comic` `2 / 2`
  - `Batgirl` `122 / 122`
- Those `179` files were promoted out of JDownloader into `/mnt/phoenix/media/incoming/mylar-import`.
- Mylar is correctly configured to watch `/mylar-imports`, and the container has been restarted and verified:
  - `check_folder = /mylar-imports`
  - `manual_pp_folder = /mylar-imports`
  - `comic_dir = /mylar-imports`
  - `download_scan_interval = 5`
- Important negative result: blind `check_folder` consumption on the full `182`-file staged basket did not work as hoped. Mylar kept reprocessing already-known runs like `Superboy & The Ravers` and `Marvel Mutts Infinity Comic` as duplicate/post-process work instead of draining the basket.
- To restore a sane staging boundary, `179` known-series files were moved out of `/mnt/phoenix/media/incoming/mylar-import` into `/mnt/phoenix/media/incoming/archive/mylar-import-cleanup/2026-04-26-known-series-duplicates`.
- The live `mylar-import` basket is now intentionally reduced to only three standalone books:
  - `52 Aftermath - The Four Horsemen v01 (2008)`
  - `Batman - Detective v01 (2007)`
  - `JLA - Salvation Run v01 (2016)`

## Practical Next Step
1. Let Mylar scan the reduced 3-file basket once and see whether those standalone books import cleanly.
2. Do not re-stage large known-series runs through `mylar-import`; use the proven series-aware or seeded known-series lanes instead.
3. Keep JDownloader as the active raw intake queue and only promote files into `mylar-import` when they are true standalone candidates for Mylar folder processing.
