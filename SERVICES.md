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

## Current Host Identity

Cirrus should currently be treated as a minimal desktop with services.

Reason:
- Debian Desktop was the only install path that completed cleanly on this hardware
- key hardware behavior such as Wi-Fi and Bluetooth came up correctly through that path
- a small local desktop remains useful for hardware recovery and direct maintenance
- Avahi is kept intentionally for `.local` discovery, but only on the wired interface

## Power Policy

Suspend is currently hard-disabled on Cirrus.

Current implementation:
- GNOME idle suspend disabled for `rmleonard`
- GNOME idle suspend disabled for the `Debian-gdm` greeter
- `/etc/systemd/logind.conf.d/90-cirrus-no-idle-suspend.conf` sets:
  - `IdleAction=ignore`
  - `IdleActionSec=0`
- `/etc/systemd/sleep.conf.d/90-cirrus-disable-sleep.conf` sets:
  - `AllowSuspend=no`
  - `AllowHibernation=no`
  - `AllowSuspendThenHibernate=no`
  - `AllowHybridSleep=no`

Reason:
- the greeter session previously triggered suspend after idle
- after resume, `mnt-phoenix.mount` was explicitly unmounted
- the host should not be allowed to sleep until this workstation-with-services baseline is stable

## Recommended Keep/Drop Baseline

This is the recommended default for Cirrus as a minimal desktop host that will also run services.

### Keep

- `ssh.service`
- `ufw.service`
- `unattended-upgrades.service`
- `NetworkManager.service`
- `wpa_supplicant.service`
- `cron.service`
- `mdmonitor.service`
- `apparmor.service`
- `gdm.service`
- `avahi-daemon.service`
- `bluetooth.service`
- `udisks2.service`
- `upower.service`
- `power-profiles-daemon.service`
- `accounts-daemon.service`
- `low-memory-monitor.service`

### Drop Unless There Is A Specific Current Use Case

- `cups.service`
- `cups-browsed.service`
- `ModemManager.service`
- `geoclue.service`
- `colord.service`
- `switcheroo-control.service`

### Avahi Policy

Keep `avahi-daemon`, but restrict it to the wired interface.

Current implementation:
- `/etc/avahi/avahi-daemon.conf`
- `allow-interfaces=enp1s0`

Reason:
- preserve the convenience of `cirrus.local`
- avoid resolving the host to the Wi-Fi address when wired is the preferred stable path

### Open Decision

- `NetworkManager-wait-online.service`

Recommendation:

- disable it unless a specific boot dependency actually needs network-online semantics

## Recommended Order Of Service Cleanup

1. Remove only `cups` and `cups-browsed` first, since local printing is explicitly not needed.
2. Verify desktop, network, and host access still behave normally.
3. Reassess `ModemManager`, `geoclue`, `colord`, and `switcheroo-control` one by one instead of treating the entire desktop stack as expendable.
4. Capture another state snapshot after the prune.

## Docker Baseline

## Current State

- Docker is not installed on Cirrus
- no Docker or containerd packages are present
- no Docker or containerd services are enabled
- host firewall backend is `iptables-nft`
- UFW is enabled

## Install Source

Use Docker's official Debian repository, not Debian's `docker.io` package.

Reason:
- current upstream packaging for `docker-ce`, `containerd.io`, `docker-buildx-plugin`, and `docker-compose-plugin`
- clearer upgrade path
- matches current Docker official Debian guidance

Packages:
- `docker-ce`
- `docker-ce-cli`
- `containerd.io`
- `docker-buildx-plugin`
- `docker-compose-plugin`

## Runtime Model

Use rootful Docker, not rootless Docker, for the initial Cirrus baseline.

Reason:
- simpler operation with bind mounts into Phoenix
- fewer surprises around service ownership and shared media access
- easier to align with systemd service management and current host posture

Operational note:
- do not add `rmleonard` to the `docker` group by default
- use `sudo docker ...` unless there is a specific operational reason to grant root-equivalent Docker access to the user account

## Data Placement

Keep Docker daemon state on the root filesystem for now.

Recommendation:
- keep Docker `data-root` at the default `/var/lib/docker`
- keep persistent application data on Phoenix via bind mounts

Reason:
- root filesystem is NVMe RAID1 and nearly empty
- Docker image layers and ephemeral writable layers benefit from faster and redundant local storage
- Phoenix should hold durable service data, media, backups, and staging content

Phoenix bind mount targets:
- `/mnt/phoenix/services/kavita`
- `/mnt/phoenix/services/mylar`
- `/mnt/phoenix/media/comics`
- `/mnt/phoenix/media/books/...`
- `/mnt/phoenix/media/incoming`

## Daemon Configuration

Recommended `/etc/docker/daemon.json` baseline:

```json
{
  "log-driver": "local",
  "live-restore": true
}
```

Reason:
- Docker documents `local` as the recommended default logging driver for general use because it rotates logs and reduces disk-exhaustion risk
- `live-restore` reduces service disruption during daemon restarts

Not recommended yet:
- changing `data-root`
- disabling Docker firewall management
- exposing the Docker API remotely

## Networking And Firewall

Important constraint from Docker's official docs:
- published container ports bypass normal UFW filtering behavior

Baseline recommendation:
- do not publish container ports casually
- prefer a reverse proxy pattern for web services
- if published ports are needed, control them deliberately with Docker-aware firewall rules rather than assuming UFW alone will protect them
- do not set `"iptables": false` in `daemon.json`

## Compose Policy

Use `docker compose` as the canonical deployment method.

Recommendation:
- one compose project per service or tightly related service group
- keep compose files in a tracked host path such as `/srv/compose`
- keep secrets out of git
- use explicit bind mounts into Phoenix for durable data

## Pre-Install Checklist

Before installing Docker:
- complete the first pass of service pruning from the current desktop-heavy baseline
- keep the current Phoenix ownership and ACL baseline
- keep SMART monitoring enabled for Phoenix and both NVMe devices
- confirm the intended ports for Kavita and Mylar before any publish rules are added
