---
name: host-truth-capture
description: Capture and document current Linux host truth from live system state. Use when a user wants to inspect a machine, verify mounts/services/network/firewall/storage, create or refresh current-state documentation, or establish an authoritative host baseline before making changes.
---

# Host Truth Capture

## Overview

Establish current host truth from live inspection, not assumptions or old notes. Use this skill to build or refresh a host baseline before storage changes, hardening work, service deployment, or restart handoff updates.

## Workflow

1. Read the host's existing top-level truth docs first.
2. Inspect the live host state.
3. Compare live state with the current docs.
4. Update the docs so implemented truth is clear and current.
5. Save a snapshot or note any unresolved drift.

## Start With Existing Docs

Read only the documents needed to understand current truth and where to write updates:

- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `RESUME.md`
- the latest saved host snapshot file
- any storage or hardening note directly relevant to the task

Do not bulk-load every root doc unless the task really needs it.

## Inspect Live State

Prefer direct, inspectable commands. Typical checks:

- host identity: `hostnamectl`, `uname -a`
- filesystems: `findmnt`, `lsblk -f`, `df -hT`
- storage-specific checks: `btrfs filesystem show`, `btrfs subvolume list`
- services: `systemctl is-enabled`, `systemctl is-active`, `systemctl --failed`
- network: `ip -br addr`, `ip r`
- firewall: `ufw status verbose`
- hardware monitoring: `smartctl --scan-open`, `systemctl status smartmontools`
- session and suspend troubleshooting: `journalctl -b`, `loginctl list-sessions`

When the task is risky or the host state could have changed recently, prefer live commands over old snapshots.

## Writeback Rules

Update docs so they reflect implemented reality:

- `CURRENT_STATE.md` for implemented truth
- `SERVICES.md` for service baseline or host identity
- `logical_storage.md` or equivalent for storage roles and layout
- `Action-Log.md` for significant actions and verification steps
- `RESUME.md` if the work affects next-session restart context

Prefer concise statements of fact:

- what is true now
- what was verified live
- what remains unresolved
- what changed because of the work

## Snapshot Guidance

When a major baseline changes, capture a timestamped state snapshot in the repo root.

Use the reference file for a reusable host snapshot command set.

## Guardrails

- Do not treat old notes as truth when live inspection disagrees.
- Do not claim a future design is implemented.
- Do not introduce services before storage and hardening are documented.
- Do not make destructive storage changes just to “simplify” the truth capture.

## Resources

- `references/linux-host-snapshot.md`
  Use for a compact reusable checklist of host-inspection commands and what each class of command is for.
  Read this when building or refreshing a host snapshot.
