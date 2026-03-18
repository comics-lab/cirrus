---
name: service-baseline-review
description: Review and document a Linux host service baseline before adding higher-level application stacks. Use when a user needs to classify enabled services, decide keep versus review versus remove, align services with host identity, or prepare a documented service posture before Docker or other deployments.
---

# Service Baseline Review

## Overview

Turn a vague list of running services into a deliberate host service policy. Use this skill to identify what the machine is trying to be, decide which services are intentional, and document the keep or review or remove set before layering on more infrastructure.

## Workflow

1. Read the current host truth, service docs, and latest snapshot.
2. Inspect the live enabled and active units.
3. Classify services by role and risk.
4. Decide changes only after the host identity is explicit.
5. Record the resulting baseline and any deferred review items.

## Start With

- `CURRENT_STATE.md`
- `SERVICES.md`
- `SETUP_PLAN.md`
- latest host snapshot file
- hardening notes if service review is part of a hardening pass

## Inspect Live Services

Typical commands:

- `systemctl list-unit-files --state=enabled --no-pager`
- `systemctl --type=service --state=running --no-pager`
- `systemctl is-enabled <unit>`
- `systemctl is-active <unit>`
- `journalctl -b --no-pager` when service behavior changed after boot or resume

Do not rely on package presence alone. Prefer enabled and active state, plus the host role the service supports.

When the user asks about remote file access:

- prefer reviewing whether the existing SSH service can satisfy the need through `SFTP`
- avoid adding `FTP`, `FTPS`, `WebDAV`, or `SMB` by default just because a client supports them
- treat any new network file-sharing daemon as a new service-baseline decision, not a convenience toggle

## Classification Model

Classify each reviewed service as one of:

- `required`
  Needed for boot, storage, networking, remote access, or the documented host role
- `intentional convenience`
  Deliberately kept because it supports a minimal desktop or a useful local feature
- `unclear`
  Present but the reason is not yet documented or proven
- `remove candidate`
  Adds surface area without supporting the documented host role

## Decision Order

Make decisions in this order:

1. What is the host identity?
2. Which services are required by that identity?
3. Which services are convenience features worth keeping?
4. Which services are merely inherited defaults?
5. Which services are safe to remove now, and which should be deferred until after validation?

Do not remove services first and rationalize later.

## Writeback Rules

Update:

- `SERVICES.md` for the keep or review or remove baseline
- `CURRENT_STATE.md` if the host identity or implemented service posture changed
- `SETUP_PLAN.md` if service review unblocks later work
- `Action-Log.md` for significant changes and verification
- `RESUME.md` if the next session must validate service behavior after reboot or login

## Guardrails

- Do not let package metapackages drive host-identity decisions.
- Do not strip desktop support from a machine that needs it for hardware stability.
- Do not assume a running service is intentional just because it is active.
- Prefer small review waves and post-change verification over aggressive pruning.

## Resources

- `references/service-classification.md`
  Use for a reusable review model for required services, convenience services, unclear services, and remove candidates.
