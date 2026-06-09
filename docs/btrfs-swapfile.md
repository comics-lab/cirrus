# Btrfs Swapfile Setup

This note records the safe way to create and activate a swapfile on the Cirrus Btrfs root filesystem.

The important design choice is:

- keep the swapfile in its own dedicated Btrfs subvolume
- do not snapshot that subvolume
- do not place the swapfile on a snapshotted subvolume

That avoids the common Btrfs swapfile pitfalls and keeps the swap area isolated from the rest of the system volume.

## Current Host Context

Observed on Cirrus:

- root filesystem: Btrfs
- `/swapfile` exists today
- `/etc/fstab` already contains `/swapfile none swap defaults 0 0`
- the current `/swapfile` is not active
- `swapon /swapfile` previously failed because the file is not yet set up in a Btrfs-safe way

The goal of this document is to replace that ad hoc file with a clean dedicated swap subvolume and a new swapfile under it.

## Target Layout

Use this layout:

- Btrfs filesystem mounted at `/`
- dedicated subvolume mounted at `/swap`
- swapfile at `/swap/swapfile`

Do not snapshot `/swap`.

## Step 1: Confirm the Root Filesystem Is Writable

Check the mount state:

```bash
mount | grep ' on / '
```

The root filesystem must be mounted read-write before you create or activate the new swapfile.

## Step 2: Create the Dedicated Swap Subvolume

Create a mountpoint if it does not exist:

```bash
sudo mkdir -p /swap
```

Create the Btrfs subvolume:

```bash
sudo btrfs subvolume create /swap
```

If `/swap` already exists as a normal directory, remove or rename it before creating the subvolume.

On the current Cirrus layout, the swap subvolume is nested under the `@` root subvolume, so it shows up as `@/swap`. If you are using the same layout, the mount entry must point at the nested path or the subvolume ID, not a top-level `swap` name.

## Step 3: Add the Subvolume to `/etc/fstab`

Add a Btrfs mount entry for the dedicated swap subvolume.

Example:

```fstab
UUID=<your-btrfs-uuid>  /swap  btrfs  subvol=@/swap,noatime  0  0
```

If the path form is ambiguous, use the subvolume ID instead:

```fstab
UUID=<your-btrfs-uuid>  /swap  btrfs  subvolid=258,noatime  0  0
```

Adjust the value to match the actual mounted subvolume on this host.

Then mount it:

```bash
sudo mount /swap
```

or:

```bash
sudo mount -a
```

## Step 4: Create the Swapfile

Preferred method, if available:

```bash
sudo btrfs filesystem mkswapfile --size 16G /swap/swapfile
```

If that helper is not available, use the manual fallback:

```bash
sudo btrfs property set /swap compression none
sudo chattr +C /swap
sudo fallocate -l 16G /swap/swapfile
sudo chmod 600 /swap/swapfile
sudo mkswap /swap/swapfile
```

The important points are:

- disable compression for the location
- ensure the file is not COW-managed
- set mode `600`
- initialize it with `mkswap`

## Step 5: Activate the Swapfile

```bash
sudo swapon /swap/swapfile
```

## Step 6: Make It Persistent

Keep the swap entry in `/etc/fstab`:

```fstab
/swap/swapfile none swap defaults 0 0
```

## Step 7: Verify the Setup

Check that swap is active:

```bash
swapon --show
```

Check memory and swap totals:

```bash
free -h
```

Optional Btrfs-specific verification:

```bash
btrfs inspect-internal map-swapfile /swap/swapfile
```

## Optional: Force Swap Pressure for zswap Testing

If you want to verify zswap activity, run the bundled pressure test in a second terminal:

```bash
python3 /home/rmleonard/Projects/cirrus/utilities/zswap_pressure_test.py --target-mib 12000 --hold-seconds 60
```

While that runs, watch:

```bash
watch -n 1 'cat /sys/kernel/debug/zswap/stored_pages; echo ---; cat /sys/kernel/debug/zswap/pool_total_size; echo ---; swapon --show; echo ---; free -h'
```

If the system becomes sluggish, stop the test early. Start with a smaller `--target-mib` value if needed.

## Important Rules

- Do not snapshot the swap subvolume.
- Do not balance the filesystem while the swapfile is active.
- If you need to rebuild the swapfile, run `swapoff /swap/swapfile` first.
- Keep swapfile maintenance separate from general host snapshots.

## Recovery Path

If the existing `/swapfile` is still present at the filesystem root, treat it as disposable once the dedicated subvolume is ready.

Recommended cleanup sequence:

```bash
sudo swapoff /swapfile 2>/dev/null || true
sudo rm -f /swapfile
```

Then create the new swapfile under `/swap`.

## Summary

The safe Cirrus approach is:

1. writable Btrfs root
2. dedicated `/swap` subvolume
3. swapfile inside that subvolume
4. `mkswap`
5. `swapon`
6. verify with `swapon --show`

This keeps swap isolated and avoids the usual Btrfs swapfile pitfalls.
