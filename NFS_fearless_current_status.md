# NFS Fearless Current Status

Current date: `2026-04-17`

## Current Status

Cirrus is back on the correct direct export:

```text
reality.local:/mnt/fearless -> /mnt/fearless
```

The mounted tree on Cirrus now matches the expected top level on `reality.local`:

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

The remaining broken path is the separate bind-export:

```text
reality.local:/export/fearless
```

That path currently mounts as an empty directory from Cirrus.

The previously commented bind-mount block in `reality.local:/etc/fstab` lines `44` through `57` has now been restored, including the dependent `longbox`, `shortbox`, `FLBM-*`, and selected `grackle` library paths. The final line required a source-path typo fix from `Mylar-Shortbox-ROO` to `Mylar-Shortbox-ROOT`.

## What Was Verified

### On Cirrus

- `/etc/fstab` entry is correct:

```fstab
reality.local:/mnt/fearless /mnt/fearless nfs defaults,_netdev,nofail 0 0
```

- remounting `/mnt/fearless` did not help
- mounting to a fresh alternate client path `/mnt/fearless-test` still showed the same wrong tree
- forcing NFSv3 instead of NFSv4 still showed the same wrong tree
- `showmount -e 192.168.1.126` currently advertises both `/mnt/fearless` and `/export/fearless`
- a fresh privileged mount of `192.168.1.126:/mnt/fearless` on a temporary probe path returned the expected `A/books/comics/...` tree
- a fresh privileged mount of `192.168.1.126:/export/fearless` on a separate temporary probe path returned an empty directory
- Cirrus was then restored to the intended live mount:

```bash
sudo mount /mnt/fearless
findmnt /mnt/fearless
ls -la /mnt/fearless | sed -n '1,80p'
```
- After the `fstab` bind-mount block was restored on `reality.local`, Cirrus re-verified these direct exports over NFSv4:
  - `/mnt/DC`
  - `/mnt/shortbox`
  - `/mnt/longbox`
  - `/mnt/fearless`
- `/mnt/longbox` initially failed from Cirrus over NFSv4 with `Stale file handle`, while a one-off NFSv3 mount succeeded.
- Restarting `nfs-server` on `reality.local` cleared the NFSv4 `longbox` failure; after restart, the fresh NFSv4 probe mount worked.

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
- `showmount -e localhost` continues to advertise the expected exports after the bind-mount restore and NFS restart
- odd but non-blocking result: `/proc/fs/nfsd/exports` remained effectively empty during later checks even while `showmount` and real client mounts were working

## Workaround Attempted

A fresh bind-export path was created on `reality.local`:

```bash
sudo mkdir -p /export/fearless
sudo mount --bind /mnt/fearless /export/fearless
```

The live recheck on `2026-04-17` narrowed that result further: `reality.local:/export/fearless` currently mounts as an empty directory, not as the correct `fearless` tree.

## Current Conclusion

- `reality.local:/mnt/fearless` is the correct export for Cirrus and is currently working
- the restored bind-mounted exports are also working again for Cirrus over NFSv4
- `reality.local:/export/fearless` is still broken server-side
- the stale Cirrus-side test mount has been removed
- the temporary NFSv4 `longbox` failure was resolved by restarting `nfs-server`
- the remaining problem is no longer "fearless is unavailable on Cirrus"; it is specifically "the optional bind-export path on reality.local does not present the expected object"

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
- decide whether `/export/fearless` should be repaired or removed entirely
- leave Cirrus using `reality.local:/mnt/fearless` unless a concrete server-side reason appears to change that
- if `longbox` shows another NFSv4 stale-handle event after future mount-graph changes, restart `nfs-server` before doing deeper surgery
