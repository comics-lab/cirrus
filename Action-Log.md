# Action Log — cirrus

## 2026-01-26
- Added AGENTS.md to align with org master directives.
- Started local logging files: CONVERSATION.md, BOOKMARKS.md, Action-Log.md.

## 2026-01-26
- Installed and enabled unattended-upgrades; configured journald persistent storage; verified logrotate.timer.
- Populated Cirrus physical inventory docs under the_lab/comics-lab-book/01-physical/.
- Saved RESUME.md for next session.

## 2026-03-15
- Parsed root documentation and operational snapshots to assess repo scope and next steps.
- Recorded recommendation to move the repo to `~/Projects/cirrus`, replace `AGENTS.md`, add `README.md`, and finish host setup before resuming comics-lab architecture work.
- Rewrote `AGENTS.md` for Cirrus host scope and added a root `README.md` that points to local logs and setup docs.
- Added `CURRENT_STATE.md` and `SETUP_PLAN.md` as the new top-level entry points for current truth and forward work.
- Reindexed the root docs and normalized stale path references so restart guidance matches the current repo location.
- Pushed branch `docs-normalization` to GitHub and left branch-diff review pending before merge.
- Verified the live enabled and running service set on Cirrus and added `SERVICES.md` to capture the workstation-vs-server decision point.
- Captured a fresh live state snapshot in `state-of-hardware-20260315-220018.txt` and documented that Phoenix still looks like legacy/recovery data rather than clean service storage.
- Wiped and recreated Phoenix as a fresh Btrfs volume labeled `phoenix`, updated `/etc/fstab`, and remounted it with `noatime,compress=zstd:3`.
- Installed `smartmontools` and `gdisk`, then replaced the default `DEVICESCAN` config with explicit SMART monitoring for Phoenix and both NVMe devices.
- Created the selected lean Phoenix Btrfs subvolume layout, including the `books/ebooks` and `books/other` subtree.
- Documented the Phoenix ownership map using a shared `media` group for both services and manual operator access.
- Applied the Phoenix shared-group baseline: created group `media`, added `rmleonard`, set shared trees to `root:media`, enabled setgid directories, and added default ACLs.
- Captured a fresh post-change state snapshot in `state-of-hardware-20260315-230117.txt` after the Phoenix rebuild, SMART setup, and ACL baseline.
- Merged `docs-normalization` into `main` and documented the initial Docker baseline in `SERVICES.md`.
- Added a reboot-watch note to `RESUME.md` to check Phoenix auto-mount behavior and the `plymouth-quit-wait.service` boot stall on the next login.
- Removed the stale `~/.npm-global` Codex install, reinstalled Codex under the active `nvm` global prefix, cleared stale `~/.codex/tmp/arg0` state, and verified `codex-cli 0.114.0`.
- Verified after reboot that Phoenix auto-mounted successfully, network came up, and Codex resolved from the standardized `nvm` path.
- Updated the service baseline to treat Cirrus as a minimal desktop with services rather than a server to be stripped aggressively.
- Removed the CUPS stack and restricted Avahi to `enp1s0` so `cirrus.local` resolves to the wired address instead of Wi-Fi.
- Updated `RESUME.md` with the next reboot validation plan: one-hour idle test, remote login first, local login second, then Bluetooth validation before moving on to Docker.
- Determined that the `Debian-gdm` greeter was still triggering suspend on idle; disabled GNOME idle suspend for the greeter and hard-disabled suspend/hibernate system-wide.
- Confirmed that Phoenix was being unmounted during resume from suspend, remounted it manually, and documented suspend as the cause rather than boot mount failure.
- Verified the post-fix reboot test: the host stayed awake for about one hour, Phoenix remained mounted, remote and local login both worked, Bluetooth worked, and `cirrus.local` remained valid.
- Drafted the first reusable host-operation skill sources under `skills/`: `host-truth-capture`, `host-resume-handoff`, `host-storage-baseline`, and `host-hardening-baseline`.
- Verified administrative SFTP access from FileBrowser Pro on iOS using a dedicated ED25519 key, with a temporary password-auth window used only to retrieve/import the key file before re-locking Cirrus to key-only SSH.
- Noted a separate `reality.local` recovery issue: the host is dropping into emergency mode because volume `fearless` is offline, with many dependent bind mounts likely declared in `/etc/fstab`; recommended first-pass recovery is to remount `/` read-write, back up `/etc/fstab`, comment out the `fearless` UUID mount and all bind mounts that depend on it, then reboot and restore mounts deliberately later.
- Confirmed that `reality.local` is back online, so the temporary `fearless` emergency-mode recovery note can be cleared from active follow-up.
- Refined the Phoenix storage policy for the intended large multi-application library model: acquisition tools should write to `media/incoming`, curated library trees should keep a single designated writer, reader/display apps should treat library trees as read-only where possible, and the current Phoenix layout should be treated as the path-policy baseline rather than proof that final 20TB-plus capacity is already solved.
- Added two permanent NFS workflow mounts from `reality.local` on Cirrus: `/mnt/old_library` from `/mnt/grackle` and `/mnt/incoming-root` from `/home/Various-Downloads`; documented them as external source mounts that feed the local ingest workflow without replacing Phoenix as the durable storage baseline.
- Added a canonical Phoenix source-path namespace under `media/sources/` with `legacy_mylar` and `upstream_incoming` so Docker bind-mount planning can refer to stable local source-class paths without redefining Phoenix as an external-NFS-backed store.
- Installed Docker from Docker's official Debian repository, enabled the daemon, applied the minimal `/etc/docker/daemon.json` baseline (`log-driver=local`, `live-restore=true`), and stopped at the boundary before any application containers were deployed.
- Reviewed the legacy `reality.local` JDownloader service and translated its use case into a cleaner Cirrus plan: JDownloader 2 should be the first Dockerized intake service, writing only to intake paths on Phoenix, with persistent app state kept under `/mnt/phoenix/services/jdownloader2` and no direct write access to curated library trees.
- Chose MyJDownloader only for the initial Cirrus JDownloader deployment and explicitly rejected exposing a local browser UI at first.
- Created `/mnt/phoenix/media/incoming/jdownloader` as the dedicated first-stage JDownloader intake path and documented the branching rule that valid `ComicInfo.xml` goes toward Mylar-oriented processing while files without valid metadata go to alternate processing.
- Created `/mnt/phoenix/services/jdownloader2` and documented the first-pass JDownloader Compose spec using `jlesage/jdownloader-2`, `USER_ID=1000`, `GROUP_ID=1001`, `UMASK=002`, MyJDownloader-only control, and bind mounts limited to `/config` and `/output`.
- Deployed the first JDownloader container from `/srv/compose/jdownloader2/docker-compose.yml` with `TZ=America/Los_Angeles`, no published browser UI port, and verified that the container starts cleanly and initializes its state under `/mnt/phoenix/services/jdownloader2` as `rmleonard:media`.
- Validated `jdownloader2` as the first working intake service on Cirrus: LAN-only browser UI is available at `192.168.1.113:5800`, MyJDownloader sees the device, downloads land in `/mnt/phoenix/media/incoming/jdownloader`, and freshly downloaded files can be moved or deleted successfully.
