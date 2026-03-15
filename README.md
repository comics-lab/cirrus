# Cirrus

This repo is the working notebook and operational documentation for the `cirrus` machine.

Cirrus is currently in setup and configuration. Until that work is complete, this repo should describe present host reality first and future lab architecture second.

## Purpose

Use this repo to track:

- host state and hardware snapshots
- storage layout and mount decisions
- security hardening status
- service deployment prerequisites and baselines
- local runbooks, notes, and setup history

This repo is not the source of truth for comics-lab organization policy. It may later feed a broader lab-architecture project after Cirrus is stable.

## Start Here

- `CURRENT_STATE.md`: concise implemented truth for the host
- `SETUP_PLAN.md`: ordered next work for Cirrus
- `SERVICES.md`: current live service baseline and keep/drop review queue
- `RESUME.md`: normalized session handoff for the next restart
- `NEXT_STEPS_2026-03-15.md`: restructuring assessment and rationale
- `state-of-hardware-20260315-220018.txt`: current live host snapshot
- `state-of-hardware-20260126-055629.txt`: baseline host snapshot
- `cirrus_checklist.md`: older staged bring-up checklist
- `hardening.md`: detailed hardening notes
- `logical_storage.md`: storage roles and rules

## Index

Current root docs:

- `AGENTS.md`: repo-scoped operating guidance for agents
- `README.md`: repo purpose and navigation
- `CURRENT_STATE.md`: implemented host truth
- `SETUP_PLAN.md`: ordered remaining work
- `SERVICES.md`: service inventory and baseline decision point
- `RESUME.md`: next-session restart point
- `NEXT_STEPS_2026-03-15.md`: March restructuring rationale

Reference and working notes:

- `state-of-hardware-20260315-220018.txt`: latest captured live host snapshot
- `state-of-hardware-20260126-055629.txt`: captured host snapshot
- `cirrus_checklist.md`: older bring-up checklist with captured state
- `hardening.md`: hardening checklist plus observed status
- `logical_storage.md`: storage roles plus current implementation notes
- `restart.md`: January restart checkpoint
- `REPLY_beast-storage-plan_20260125-2147.txt`: saved external planning note

## Logs

- `CONVERSATION.md`
- `BOOKMARKS.md`
- `Action-Log.md`

## Documentation Notes

The root documentation still contains some older working notes, but the intended structure is now:

- keep host truth and setup tasks at the root
- keep larger lab book material under `the_lab/`
- move org-wide architecture work into a separate project after Cirrus setup is complete
