# Transmission Docker Installation

Deferred runbook for installing Transmission as a Docker service on Cirrus. This procedure
is intended for downloading weekly comic packs only. It does not install or start anything
by itself.

## Current Capacity Assessment

The last live check showed:

- Phoenix: approximately `1.8 TB` free on a `3.7 TB` Btrfs filesystem
- Cirrus CPU: `4` logical processors
- Cirrus memory: `15 GiB` RAM with approximately `12 GiB` available
- Active services: JDownloader2, Mylar3, and Kavita
- Active swap: a `16 GiB` Btrfs swapfile on the NVMe RAID1 stack

The observed container snapshot used approximately `14%` combined CPU and `2.2 GiB` RAM.
Transmission is expected to add little CPU or memory pressure. Network bandwidth, torrent
piece writes, extraction, and archive processing are the meaningful constraints.

## Storage Design

The NVMe devices are not a native Btrfs RAID pair. They are members of an `mdadm` RAID1
device, with Btrfs on top:

```text
/dev/nvme0n1p1 ─┐
                ├─ /dev/md0 RAID1 ─ /dev/md0p1 ─ Btrfs
/dev/nvme1n1p2 ─┘
```

Use the fast redundant stack for transient torrent writes and Phoenix for completed packs:

```text
NVMe RAID1/Btrfs:  /srv/transmission/incomplete
Phoenix Btrfs:     /mnt/phoenix/media/incoming/torrents/weekly
```

This isolates random torrent piece writes from JDownloader, extraction, and CBZ processing.
When a torrent completes, Transmission performs a cross-filesystem copy to Phoenix. That
adds a full completion write, but it keeps partial files out of the intake tree and places
the durable source where the existing workflow expects it.

This is redundancy and I/O isolation, not backup. Completed packs still require the normal
archive and intake handling.

Before proceeding, verify the actual writable mountpoints and available space:

```bash
df -hT /mnt/phoenix
df -hT /srv/transmission
findmnt -T /mnt/phoenix
findmnt -T /srv/transmission
```

## Image

Use LinuxServer's maintained Transmission image:

```text
lscr.io/linuxserver/transmission:latest
```

Reference: <https://hub.docker.com/r/linuxserver/transmission/>

Pin a tested image tag after the first successful deployment rather than relying forever on
`latest`.

## Planned Paths

Create or confirm these paths before deployment:

```text
/srv/compose/transmission/
/srv/transmission/config/
/srv/transmission/incomplete/
/mnt/phoenix/media/incoming/torrents/weekly/
/mnt/phoenix/media/incoming/torrents/archive/
```

The configuration directory must be on durable storage. The incomplete directory should be
on the NVMe RAID1/Btrfs stack. Completed weekly packs and their archive history belong on
Phoenix.

## Compose Template

Create `/srv/compose/transmission/docker-compose.yml` with values appropriate to the live
host. Replace the UID/GID after checking the account and group used by the other media
services.

```yaml
services:
  transmission:
    image: lscr.io/linuxserver/transmission:latest
    container_name: transmission
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
      - TRANSMISSION_WEB_HOME=
      - USER=replace-me
      - PASS=replace-me
    volumes:
      - /srv/transmission/config:/config
      - /srv/transmission/incomplete:/downloads/incomplete
      - /mnt/phoenix/media/incoming/torrents/weekly:/downloads/complete
      - /mnt/phoenix/media/incoming/torrents/archive:/watch
    ports:
      - 192.168.1.113:9091:9091
      - 51413:51413
      - 51413:51413/udp
    restart: unless-stopped
```

Do not expose the Web UI beyond the trusted LAN without an explicit access-control plan.
Use a strong RPC password and restrict the RPC whitelist to the local network as supported
by the image configuration.

## Deferred Installer Procedure

Run these steps only when installation is approved.

### 1. Capture current state

```bash
docker ps
df -hT /mnt/phoenix
df -hT /srv/transmission
free -h
nproc
```

Record the output in the action log before creating the service.

### 2. Verify ownership and paths

```bash
id rmleonard
getent group docker
sudo mkdir -p /srv/compose/transmission
sudo mkdir -p /srv/transmission/config /srv/transmission/incomplete
mkdir -p /mnt/phoenix/media/incoming/torrents/weekly
mkdir -p /mnt/phoenix/media/incoming/torrents/archive
```

Use the same intended service UID/GID and group policy as Mylar and the other media
containers. Do not apply broad world-writable permissions.

### 3. Write and review Compose configuration

```bash
cd /srv/compose/transmission
nano docker-compose.yml
docker compose config
```

Review port bindings, credentials, UID/GID, and all four volume paths before starting.

### 4. Pull and start

```bash
docker compose pull transmission
docker compose up -d transmission
docker compose ps
docker compose logs --tail=100 transmission
```

### 5. Configure weekly-only behavior

In Transmission, configure:

- one or two active downloads maximum
- a download directory of `/downloads/complete`
- incomplete directory of `/downloads/incomplete`
- download queue enabled
- upload and download limits appropriate to the home network
- watch directory only if torrent files are intentionally placed there
- automatic removal only after the completed pack is verified

Do not point Transmission at `jdownloader`, `mylar-import`, `mylar-imports`, or `comics`.

### 6. Validate the handoff

Confirm that a test torrent creates pieces only under the incomplete path and that the
completed payload lands under Phoenix:

```bash
find /srv/transmission/incomplete -maxdepth 2 -type f -print
find /mnt/phoenix/media/incoming/torrents/weekly -maxdepth 2 -type f -print
```

Only after completion should the normal weekly workflow be run:

1. inspect the downloaded pack
2. run the weekly-aware ZIP extraction utility
3. leave weekly archives in place when required by the weekly-pack rule
4. convert CBR to CBZ where applicable
5. audit and run the intake pipeline

### 7. Monitor resource impact

```bash
docker stats --no-stream transmission jdownloader2 mylar3 kavita
df -hT /srv/transmission /mnt/phoenix
```

If disk pressure or I/O contention appears, reduce active torrents before changing service
limits. Do not treat swap usage as a substitute for sufficient free disk space.

## Rollback

To stop and remove the container while preserving configuration and downloads:

```bash
cd /srv/compose/transmission
docker compose down
```

Do not remove `/srv/transmission` or the Phoenix torrent directories during rollback. Review
and retain the configuration and completed weekly packs until the intake result is known.

## Acceptance Criteria

- [ ] Configuration persists after container recreation.
- [ ] Web UI is reachable only from the intended LAN.
- [ ] Incomplete pieces are written to the NVMe RAID1 path.
- [ ] Completed weekly packs land on Phoenix.
- [ ] Only weekly comic torrents are added.
- [ ] Active torrent count and bandwidth are bounded.
- [ ] Existing JDownloader, Mylar3, and Kavita containers remain healthy.
- [ ] The downloaded pack can enter the existing weekly intake workflow without partial files.
