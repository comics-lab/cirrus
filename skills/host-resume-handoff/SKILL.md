---
name: host-resume-handoff
description: Create clean restart checkpoints and next-session handoffs for host or ops work. Use when a user is about to stop, reboot, hand off, or resume work and needs `RESUME.md`, local logs, and the immediate next checks updated so the next session can restart safely.
---

# Host Resume Handoff

## Overview

Create a restart point that another agent or a later session can trust. Use this skill after meaningful host changes, before reboots, after unexpected incidents, or whenever the next session needs explicit first checks.

## Workflow

1. Read the current `RESUME.md` and `Action-Log.md`.
2. Summarize what changed, what is stable, and what is still risky.
3. Write the exact next-session checks in priority order.
4. Record known failure modes and the expected good state.
5. Add or update any action-log entry needed to explain the checkpoint.

## What To Update

- `RESUME.md`
  - current context
  - start-with files
  - next recommended work
  - reboot watch or validation plan when relevant
- `Action-Log.md`
  - the significant action that just happened
  - the saved checkpoint or restart note

Update `CURRENT_STATE.md` only if the checkpoint includes a real implemented-state change.

## Handoff Content Rules

Write handoff notes as operational instructions, not narrative recap.

Include:
- what is true now
- what changed in the last session
- what the next session should check first
- what must not be forgotten before proceeding

Prefer exact checks over vague reminders:

- “check whether `/mnt/data` auto-mounted”
- “run `command -v codex` and `codex --version`”
- “verify `cirrus.local` resolves to the wired address”

## When To Add A Reboot Watch

Add a reboot-watch section when:
- the host is about to reboot
- boot, suspend, mount, network, or login behavior was recently unstable
- there is a specific condition the next session must validate before proceeding

## Guardrails

- Do not leave the next session guessing what to verify first.
- Do not bury unresolved risk in a long narrative.
- Do not update resume docs as though a change is committed or pushed unless it really is.
- Distinguish between live host state, local repo state, and remote-pushed repo state when it matters.

## Resources

- `references/resume-checklist.md`
  Use for a reusable checklist of what to include in restart handoffs and what to verify after reboot or interruption.
