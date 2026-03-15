# Services — Cirrus

## Purpose

Track the current service baseline for Cirrus and identify which services are intentional, temporary, or pending removal.

## Current Live State (2026-03-15)

Verified from live `systemctl` output on Cirrus.

### Hardening-Relevant Units

- `ssh.service`: enabled and running
- `ufw.service`: enabled
- `unattended-upgrades.service`: enabled and running
- `smartmontools.service`: enabled and running
- `nftables.service`: disabled
- `fail2ban`: not installed
- `auditd`: not installed

### Identity Signal

Cirrus is currently behaving like a workstation-with-services, not a server with only temporary desktop residue.

Evidence:

- `gdm.service` running
- `NetworkManager.service` running
- `bluetooth.service` running
- `cups.service` and `cups-browsed.service` running
- `udisks2.service` running
- `upower.service` running
- `power-profiles-daemon.service` running
- `geoclue.service` running
- `colord.service` running

## Running Services That Need an Explicit Keep/Drop Decision

Likely desktop-oriented:

- `gdm.service`
- `bluetooth.service`
- `cups.service`
- `cups-browsed.service`
- `colord.service`
- `geoclue.service`
- `power-profiles-daemon.service`
- `switcheroo-control.service`
- `udisks2.service`
- `upower.service`
- `accounts-daemon.service`
- `low-memory-monitor.service`

Likely network-or-device convenience services:

- `avahi-daemon.service`
- `ModemManager.service`
- `wpa_supplicant.service`

Likely keep unless host role changes:

- `ssh.service`
- `NetworkManager.service`
- `cron.service`
- `mdmonitor.service`
- `unattended-upgrades.service`

## Enabled Units That Stand Out

From the saved and live enabled-unit lists:

- `avahi-daemon.service`
- `bluetooth.service`
- `cups.path`
- `cups.service`
- `cups-browsed.service`
- `ModemManager.service`
- `NetworkManager-wait-online.service`
- `udisks2.service`
- `wpa_supplicant.service`

## Recommended Next Step

Choose one of these as the explicit Cirrus baseline:

### Option A: Server With Temporary GNOME

Keep only what is needed for remote administration and any justified local recovery path.

Expected consequence:

- disable or remove most desktop-oriented and discovery-oriented services
- prefer wired networking only unless Wi-Fi is required as backup
- reduce local device-management conveniences

### Option B: Workstation With Services

Accept the desktop stack as intentional and harden around it.

Expected consequence:

- retain GDM and local desktop support
- keep only the subset of desktop services that are actually used
- document why both desktop and service-host behaviors are acceptable

## Decision Needed Before Docker

Do not treat the current service set as acceptable by default. The host identity needs to be documented first, then the service baseline should be pruned to match it.

## Recommended Keep/Drop Baseline

This is the recommended default if Cirrus is going to become a production-oriented host before wider lab integration resumes.

### Keep

- `ssh.service`
- `ufw.service`
- `unattended-upgrades.service`
- `NetworkManager.service`
- `wpa_supplicant.service`
- `cron.service`
- `mdmonitor.service`
- `apparmor.service`

### Keep Temporarily If Local Desktop Access Is Still Required

- `gdm.service`
- `accounts-daemon.service`
- `udisks2.service`
- `upower.service`
- `power-profiles-daemon.service`
- `low-memory-monitor.service`

### Drop Unless There Is A Specific Current Use Case

- `avahi-daemon.service`
- `cups.service`
- `cups-browsed.service`
- `bluetooth.service`
- `ModemManager.service`
- `geoclue.service`
- `colord.service`
- `switcheroo-control.service`

### Open Decision

- `NetworkManager-wait-online.service`

Recommendation:

- disable it unless a specific boot dependency actually needs network-online semantics

## Recommended Order Of Service Cleanup

1. Disable discovery and peripheral services with the weakest justification first: `avahi-daemon`, `cups`, `cups-browsed`, `ModemManager`, `bluetooth`.
2. Reboot or restart the affected units and confirm remote access still works as expected.
3. Decide whether GDM remains intentional. If not, remove the remaining desktop support stack aggressively.
4. Capture another state snapshot after the prune.
