# NFS Fearless Current Status

Current date: `2026-04-16`

## Problem

Cirrus mounts `reality.local:/mnt/fearless`, but the visible tree is wrong.

Observed on Cirrus:

```text
ddump/
input/
marvel -> /mnt/arcs/marvel/From_Longbox/Mylar-Shortbox-ROOT/marvel
marvel.here/
mrvl/
SPACE/
```

Expected on `reality.local` local shell:

```text
A/
books/
comics/
docker/
Downloads/
DOWNLOADS/
From_Longbox/
LIBRARY/
...
```

## What Was Verified

### On Cirrus

- `/etc/fstab` entry is correct:

```fstab
reality.local:/mnt/fearless /mnt/fearless nfs defaults,_netdev,nofail 0 0
```

- remounting `/mnt/fearless` did not help
- mounting to a fresh alternate client path `/mnt/fearless-test` still showed the same wrong tree
- forcing NFSv3 instead of NFSv4 still showed the same wrong tree

### On reality.local

- `/mnt/fearless` is mounted from `/dev/sde` as `btrfs`
- local shell view of `/mnt/fearless` is correct
- `rpc.mountd` namespace also sees the correct `/mnt/fearless` tree:

```bash
pid=$(pgrep -xo rpc.mountd)
sudo nsenter -t "$pid" -m findmnt /mnt/fearless
sudo nsenter -t "$pid" -m ls -la /mnt/fearless
```

- NFS services are up:
  - `nfs-server` active
  - `rpcbind` active
  - port `2049` listening
  - NFS versions `3`, `4`, `4.1`, `4.2` enabled

## Workaround Attempted

A fresh bind-export path was created on `reality.local`:

```bash
sudo mkdir -p /export/fearless
sudo mount --bind /mnt/fearless /export/fearless
```

But Cirrus mounting `reality.local:/export/fearless` still received the same wrong `ddump/input/marvel/...` tree.

## Current Conclusion

- this is not a simple Cirrus client mount issue
- this is not an NFSv4-only pseudoroot issue
- this is not explained by `rpc.mountd` seeing the wrong namespace
- the active export object presented to Cirrus is still wrong even when a fresh exported path is used

## Next Session

Continue on `reality.local`:

```bash
findmnt /export/fearless
ls -la /export/fearless | sed -n '1,80p'
sudo exportfs -v | sed -n '1,160p'
sudo cat /proc/fs/nfsd/exports
```

Goal:
- verify what `/export/fearless` looks like locally
- verify what exact export objects the kernel NFS server thinks it is serving
- only after that decide whether to rebuild the bind mount and exports again
