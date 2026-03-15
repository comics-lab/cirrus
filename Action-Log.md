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
