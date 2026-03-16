# Current State — Cirrus

## Repo Role

This repo is the working documentation and operations notebook for the `cirrus` host.

It is not the source of truth for comics-lab organization-wide governance or architecture policy.

## Host Snapshot

State captured from `state-of-hardware-20260315-230117.txt`, `state-of-hardware-20260315-220018.txt`, `state-of-hardware-20260126-055629.txt`, and related root docs.

- Hostname: `cirrus`
- OS: Debian GNU/Linux 13 (`trixie`)
- Kernel: `6.12.63+deb13-amd64`
- Repo path: `/home/rmleonard/Projects/cirrus`
- Root docs were normalized on `2026-03-15` to make this repo host-scoped
- Latest live snapshot: `2026-03-15 23:01:37 UTC`

## Storage

- Boot volume: Btrfs on `md0p1` over NVMe RAID1
- Root and home use Btrfs subvolumes: `/@` and `/@home`
- Phoenix: `/mnt/phoenix` on `/dev/sda1`
- Phoenix filesystem: Btrfs
- Phoenix size: about 3.7T
- Phoenix was recreated as a fresh Btrfs volume on `2026-03-15`
- Phoenix label: `phoenix`
- Phoenix UUID: `16dcd3d6-bfaf-4551-9c3d-ea23ecdf3481`
- Phoenix mount options: `defaults,noatime,compress=zstd:3`
- Phoenix now has an initial Btrfs subvolume layout for `media`, `services`, `backups`, and `staging`
- Phoenix application/library subvolumes currently include:
  - `media/comics`
  - `media/books/ebooks`
  - `media/books/other`
  - `media/incoming`
  - `services/kavita`
  - `services/mylar`
- Phoenix shared access baseline has been applied:
  - shared group: `media`
  - `rmleonard` is a member of `media`
  - top-level shared trees are `root:media`
  - shared directories use setgid mode `2775`
  - default ACLs grant group `media` `rwx` inheritance

## Hardening Status

Already in place:

- SSH key-only authentication
- `PermitRootLogin no`
- `PasswordAuthentication no`
- UFW enabled
- default deny incoming
- SSH allowed through firewall
- `unattended-upgrades` enabled
- journald persistent storage configured
- `logrotate.timer` enabled
- `smartmontools` installed
- `smartmontools.service` enabled and running
- explicit SMART monitoring configured for Phoenix and both NVMe devices
- Avahi is configured to advertise only on the wired interface `enp1s0` so `cirrus.local` resolves to the wired address
- system suspend is now hard-disabled through `/etc/systemd/sleep.conf.d/90-cirrus-disable-sleep.conf`
- GNOME idle suspend has been disabled for both `rmleonard` and the `Debian-gdm` greeter user

Not yet settled or incomplete:

- `fail2ban` not installed
- Docker not installed
- some nonessential services still need review
- host role is now best described as a minimal desktop with services, not a stripped server

## Network and Services

Observed at January snapshot time:

- wired and Wi-Fi were both up
- SSH enabled
- UFW enabled
- `nftables` service disabled, with UFW managing nft rules

Enabled services list includes several likely-nonessential desktop services:

- `cups`
- `cups-browsed`
- `avahi-daemon`
- `bluetooth`
- `ModemManager`

These should be reviewed before Cirrus is treated as a production service host.

Live verification on `2026-03-15` still shows a desktop-oriented active service set including:

- `gdm`
- `avahi-daemon`
- `bluetooth`
- `cups`
- `cups-browsed`
- `ModemManager`
- `udisks2`
- `upower`

This is now intentional in part: Cirrus keeps a minimal desktop and hardware-support stack because Debian Desktop provided the only clean install path for this hardware and correctly enabled key devices such as Wi-Fi and Bluetooth.

Avahi is intentionally kept for `.local` discovery, but it is restricted to the wired interface so other hosts resolve `cirrus.local` to `192.168.1.113` instead of the Wi-Fi address.

Recent operational finding:
- Phoenix mounted correctly at boot
- when the host suspended, `mnt-phoenix.mount` was explicitly unmounted during resume
- Phoenix had to be remounted manually after wake
- the mitigation in place is to disable suspend entirely until the host is stable

See `SERVICES.md` for the current review set and the adjusted keep/drop baseline.

## Documentation State

Root docs are partly redundant.

Most useful current files:

- `README.md`
- `AGENTS.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `RESUME.md`
- `NEXT_STEPS_2026-03-15.md`
- `state-of-hardware-20260315-230117.txt`
- `state-of-hardware-20260315-220018.txt`
- `state-of-hardware-20260126-055629.txt`
- `logical_storage.md`
- `hardening.md`
- `cirrus_checklist.md`

The larger book structure under `the_lab/comics-lab-book/` exists, but much of it is still stub content.

## Immediate Truths

- Cirrus setup is not complete.
- Phoenix has been reset as a clean Btrfs data volume, the initial subvolume layout exists, and the shared group/ACL baseline has been applied.
- Docker and application deployment should wait until hardening and storage decisions are finished.
- This repo should continue to document Cirrus itself, not the whole lab.
