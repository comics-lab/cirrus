# Storage Patterns

## Role Split

Default host split:
- boot volume: OS, host config, runtime binaries
- data volume: durable service data, media, backups, staging

## Btrfs Fit

Use Btrfs when you want:
- checksumming
- scrub support
- subvolume layout
- future multi-device flexibility

## Mount Planning

Typical checks:
- UUID stability
- mount options
- whether the volume should mount the filesystem root or a specific subvolume

## Ownership Planning

Good default for mixed human + service access:
- shared group
- setgid directories
- default ACLs on shared writable trees

## Service Placement

Decide before deployment:
- which paths are durable service state
- which paths are media libraries
- which paths are staging/import
- which paths should be read-only for some services
