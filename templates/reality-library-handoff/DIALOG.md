# DIALOG

Shared working notes between the `reality.local` search/index agent and the
`cirrus` import/reconciliation agent.

Use this file to capture:

- search strategy changes
- indexing assumptions
- filename parsing heuristics
- source-tree quirks
- failures and false positives
- lessons that should survive the next session

This is intentionally less rigid than `HANDOFF.md`.

## Format

Append short dated entries like:

### 2026-04-21 reality.local

- Indexed `/mnt/fearless/LIBRARY` and `/mnt/grackle/LIBRARY`.
- Found candidate for `Archie #151`; staged with `confirmed` confidence.
- Ignored one duplicate lower-resolution copy.

### 2026-04-21 cirrus

- Imported `Archie #151` into `Archie (1960)`.
- Mylar `Have / Total` changed from `546 / 553` to `547 / 553`.
- Removed `151` from `../MISSING_ISSUES.md`.

## Ground Rules

- prefer concrete facts over speculation
- record false positives when they teach something reusable
- if a heuristic proves wrong, write that down explicitly
- if a source tree has a stable naming convention, capture it here

## Why This Exists

This file is the memory bridge.

It lets separate agents on separate hosts preserve:

- search knowledge
- import knowledge
- naming heuristics
- failure patterns

without requiring perfect continuity of session state.
