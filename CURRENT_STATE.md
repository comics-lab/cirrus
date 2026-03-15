# Current State — Cirrus

## Repo Role

This repo is the working documentation and operations notebook for the `cirrus` host.

It is not the source of truth for comics-lab organization-wide governance or architecture policy.

## Host Snapshot

State captured from `state-of-hardware-20260126-055629.txt` and related root docs.

- Hostname: `cirrus`
- OS: Debian GNU/Linux 13 (`trixie`)
- Kernel: `6.12.63+deb13-amd64`
- Repo path: `/home/rmleonard/Projects/cirrus`
- Root docs were normalized on `2026-03-15` to make this repo host-scoped

## Storage

- Boot volume: Btrfs on `md0p1` over NVMe RAID1
- Root and home use Btrfs subvolumes: `/@` and `/@home`
- Phoenix: `/mnt/phoenix` on `/dev/sda1`
- Phoenix filesystem: Btrfs
- Phoenix size: about 3.7T
- Phoenix use at capture time: about 84%
- Phoenix currently appears to contain older data and is not yet a clean, deliberate service-data target

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

Not yet settled or incomplete:

- `fail2ban` not installed
- Docker not installed
- service baseline still looks desktop-heavy
- host role is not fully decided: server-with-GNOME vs workstation-with-services

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

See `SERVICES.md` for the current review set.

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
- `state-of-hardware-20260126-055629.txt`
- `logical_storage.md`
- `hardening.md`
- `cirrus_checklist.md`

The larger book structure under `the_lab/comics-lab-book/` exists, but much of it is still stub content.

## Immediate Truths

- Cirrus setup is not complete.
- Storage policy is not fully settled because Phoenix still needs an explicit decision.
- Docker and application deployment should wait until hardening and storage decisions are finished.
- This repo should continue to document Cirrus itself, not the whole lab.
