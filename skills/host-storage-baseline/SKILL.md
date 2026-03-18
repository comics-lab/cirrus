---
name: host-storage-baseline
description: Plan, implement, and document Linux host storage roles and data placement. Use when a user needs to decide volume purpose, filesystem choice, mount options, Btrfs subvolumes, ownership and ACL policy, or service-data placement before deploying applications or containers.
---

# Host Storage Baseline

## Overview

Turn raw disks and mounts into a deliberate storage model. Use this skill to separate boot and data roles, define durable service-data placement, and document the resulting layout so later service work does not drift.

## Workflow

1. Read the current storage docs and latest host snapshot.
2. Inspect the live disks, filesystems, mounts, and usage.
3. Decide storage roles before making service-placement decisions.
4. Define layout, ownership, and mount policy.
5. Update docs to record implemented reality and any remaining open decisions.

## Start With

- `CURRENT_STATE.md`
- `logical_storage.md` or equivalent
- `SETUP_PLAN.md`
- latest host snapshot file
- any hardening or services doc that depends on storage placement

## Inspect Live Storage

Typical commands:

- `lsblk -f`
- `findmnt -o SOURCE,FSTYPE,TARGET,OPTIONS`
- `df -hT`
- `blkid`
- `btrfs filesystem show`
- `btrfs subvolume list <mountpoint>`
- `smartctl --scan-open` when the device role or health matters

## Decision Order

Make decisions in this order:

1. What is the boot volume?
2. What is the durable data volume?
3. Which data should live on fast/redundant storage versus capacity storage?
4. What filesystem and mount options support that role?
5. What subvolume or directory layout is needed before services are deployed?
6. What ownership/group/ACL model allows both services and the human operator to work safely?

Do not skip directly to container or app placement before answering the storage-role questions.

## Writeback Rules

Update:

- `CURRENT_STATE.md` for implemented storage truth
- storage-specific doc such as `logical_storage.md`
- `SETUP_PLAN.md` if storage decisions unblock later work
- `Action-Log.md` for significant changes and verification
- `RESUME.md` if storage changes affect restart validation

## Guardrails

- Do not treat an old payload volume as clean service storage without inspection.
- Do not place long-lived service data before the role and ownership model are documented.
- Do not make destructive storage changes without explicit user direction.
- Prefer simple, inspectable layouts over clever abstraction.

## Resources

- `references/storage-patterns.md`
  Use for reusable guidance on storage-role splits, Btrfs layout, and shared ownership policy.
