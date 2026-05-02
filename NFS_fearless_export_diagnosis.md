# NFS Fearless Export Diagnosis

This note captures the last three diagnostic conclusions about the `reality.local:/mnt/fearless` export problem.

## 1. Fresh client mount still showed the wrong tree

That test is decisive.

A brand-new client mountpoint on Cirrus still shows the wrong tree, so the problem is on `reality.local`'s export side. Cirrus is not the issue.

Most likely cause:
- NFS is exporting the wrong server-side mount object for `/mnt/fearless`
- practically, that usually means mount-namespace / early-export behavior, not a bad client mount

The fastest next diagnostic on `reality.local` is:

```bash
pid=$(pgrep -xo rpc.mountd)
sudo nsenter -t "$pid" -m ls -la /mnt/fearless | sed -n '1,80p'
```

If that shows the old `ddump/input/marvel/mrvl/SPACE` tree, then `rpc.mountd` is in a different mount view than your shell. That would explain everything.

The fastest practical workaround is to export a fresh bind mount from a brand-new path.

On `reality.local`:

```bash
sudo mkdir -p /export/fearless
sudo mount --bind /mnt/fearless /export/fearless
echo '/export/fearless *(sync,rw,no_subtree_check,no_root_squash,anonuid=1000,anongid=1000)' | sudo tee /etc/exports.d/fearless.exports
sudo exportfs -ra
sudo exportfs -s | rg '/export/fearless|/mnt/fearless'
```

Then on Cirrus:

```bash
sudo mkdir -p /mnt/fearless-test2
sudo mount -v -t nfs4 reality.local:/export/fearless /mnt/fearless-test2
ls -la /mnt/fearless-test2 | sed -n '1,80p'
```

If `/mnt/fearless-test2` shows the correct tree, then:
- root cause is confirmed as the old `/mnt/fearless` export object on the server
- the clean fix is to keep using a fresh exported path like `/export/fearless`, or rebuild the export ordering more aggressively later

So my recommendation is:
1. run the `nsenter` check
2. if confirmed or if you want the fastest path forward, create the fresh bind export
3. test mount `/export/fearless` from Cirrus

If you want, after that works, I can help you turn it into the permanent clean export layout.

## 2. Confirmation that the export itself is wrong

Yes, that confirms it.

A fresh client mountpoint still gets the wrong tree, so the export served by `reality.local:/mnt/fearless` is not the same object your shell sees at `/mnt/fearless` on `reality`.

So stop testing on Cirrus. The next work is only on `reality.local`.

Do this there:

1. inspect `rpc.mountd`'s mount view

```bash
pid=$(pgrep -xo rpc.mountd)
sudo nsenter -t "$pid" -m ls -la /mnt/fearless | sed -n '1,80p'
```

2. if that shows the old tree, use a fresh bind-export path as the workaround:

```bash
sudo mkdir -p /export/fearless
sudo mount --bind /mnt/fearless /export/fearless
printf '/export/fearless *(sync,rw,no_subtree_check,no_root_squash,anonuid=1000,anongid=1000)\n' | sudo tee /etc/exports.d/fearless.exports
sudo exportfs -ra
sudo exportfs -s | rg '/export/fearless|/mnt/fearless'
```

3. then on Cirrus:

```bash
sudo mkdir -p /mnt/fearless-test2
sudo mount -v -t nfs4 reality.local:/export/fearless /mnt/fearless-test2
ls -la /mnt/fearless-test2 | sed -n '1,80p'
```

Why this is the right move:
- we already proved the client is not the problem
- a new exported server path gives us a new export object
- if that works, you have an immediate usable path and a proven server-side root cause

So yes: the `/mnt/fearless` export itself is poisoned/stale. Use a fresh exported path now, then clean up the underlying NFS service ordering later.

## 3. Short conclusion

Yes, that confirms it.

A fresh client mountpoint still gets the wrong tree, so the export served by `reality.local:/mnt/fearless` is not the same object your shell sees at `/mnt/fearless` on `reality`.

So stop testing on Cirrus. The next work is only on `reality.local`.

Do this there:

1. inspect `rpc.mountd`'s mount view

```bash
pid=$(pgrep -xo rpc.mountd)
sudo nsenter -t "$pid" -m ls -la /mnt/fearless | sed -n '1,80p'
```

2. if that shows the old tree, use a fresh bind-export path as the workaround:

```bash
sudo mkdir -p /export/fearless
sudo mount --bind /mnt/fearless /export/fearless
printf '/export/fearless *(sync,rw,no_subtree_check,no_root_squash,anonuid=1000,anongid=1000)\n' | sudo tee /etc/exports.d/fearless.exports
sudo exportfs -ra
sudo exportfs -s | rg '/export/fearless|/mnt/fearless'
```

3. then on Cirrus:

```bash
sudo mkdir -p /mnt/fearless-test2
sudo mount -v -t nfs4 reality.local:/export/fearless /mnt/fearless-test2
ls -la /mnt/fearless-test2 | sed -n '1,80p'
```

Why this is the right move:
- we already proved the client is not the problem
- a new exported server path gives us a new export object
- if that works, you have an immediate usable path and a proven server-side root cause

So yes: the `/mnt/fearless` export itself is poisoned/stale. Use a fresh exported path now, then clean up the underlying NFS service ordering later.
