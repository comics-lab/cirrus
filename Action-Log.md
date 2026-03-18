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
