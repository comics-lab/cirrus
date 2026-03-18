# Linux Host Snapshot

Use these commands selectively. Do not run all of them blindly if the task only needs one area.

## Identity

```bash
hostnamectl
uname -a
uptime
```

## Storage

```bash
lsblk -f
findmnt -o SOURCE,FSTYPE,TARGET,OPTIONS
df -hT
```

## Btrfs

```bash
sudo btrfs filesystem show
sudo btrfs subvolume list <mountpoint>
```

## Services

```bash
systemctl --failed --no-pager
systemctl list-unit-files --state=enabled --no-pager
systemctl --type=service --state=running --no-pager
```

## Network

```bash
ip -br addr
ip r
```

## Firewall

```bash
sudo ufw status verbose
```

## SMART

```bash
sudo smartctl --scan-open
systemctl status smartmontools --no-pager
```

## Boot/Resume Troubleshooting

```bash
sudo journalctl -b --no-pager
loginctl list-sessions
```
