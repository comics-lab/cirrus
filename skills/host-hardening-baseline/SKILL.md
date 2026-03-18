---
name: host-hardening-baseline
description: Review, improve, and document a Linux host hardening baseline before service deployment. Use when a user needs to verify SSH, firewall, logging, SMART, suspend/power policy, risky enabled services, or other host-level security and reliability settings before installing application stacks.
---

# Host Hardening Baseline

## Overview

Establish the host-level security and reliability baseline before higher-level services are introduced. Use this skill to verify what is already in place, identify the most important gaps, and document the resulting hardening posture.

## Workflow

1. Read the current host truth, service baseline, and latest snapshot.
2. Inspect the live hardening-relevant settings.
3. Separate essential fixes from optional tightening.
4. Apply only the changes appropriate for the host identity.
5. Record the resulting posture and any remaining gaps.

## Start With

- `CURRENT_STATE.md`
- `SERVICES.md`
- `SETUP_PLAN.md`
- `hardening.md` if present
- latest host snapshot file

## Inspect Live Hardening State

Typical checks:

- `systemctl is-enabled` and `systemctl is-active` for SSH, firewall, unattended upgrades, SMART, and candidate review services
- `sshd -T` for SSH auth posture
- `ufw status verbose`
- `systemctl --failed --no-pager`
- `journalctl -b` for boot/resume anomalies
- `smartctl --scan-open`
- power policy checks through `systemd-logind`, `sleep.conf`, and desktop power settings when the host has a GUI

## Hardening Categories

Review in this order:

1. Remote access: SSH auth, root login, firewall
2. Host reliability: logging, unattended upgrades, SMART, boot stability
3. Power behavior: suspend, resume, and unattended idle behavior
4. Service surface: enabled units that do not match the host role
5. Optional tightening: `fail2ban`, `auditd`, or other extras if justified

## Scope Rule

Do not apply server-only austerity blindly to a machine that intentionally keeps a minimal desktop for hardware support. Match the hardening baseline to the documented host identity.

## Writeback Rules

Update:

- `CURRENT_STATE.md` for the implemented posture
- `SERVICES.md` if service keep/drop guidance changed
- `hardening.md` for checklist-style status
- `Action-Log.md` for significant changes and verification
- `RESUME.md` if the next session needs explicit stability checks

## Guardrails

- Do not add new services while hardening is still unsettled.
- Do not let desktop convenience silently override host reliability.
- Prefer first fixing the causes of instability over repeatedly recovering from them.
- Distinguish between “not installed,” “installed but disabled,” and “enabled and active.”

## Resources

- `references/hardening-checks.md`
  Use for a reusable checklist of host-level checks: SSH, firewall, logging, SMART, suspend policy, and risky enabled services.
