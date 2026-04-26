# AGENTS.md — Fearless Library

This directory is a working library root on `reality.local`.

## Scope

Use this directory for:
- library inventory and cleanup work
- missing-issue tracking
- publisher-level organization checks
- handoff notes for future Codex sessions working directly in this tree

Do not use this directory for:
- host-wide Cirrus or reality infrastructure policy
- Docker or service deployment notes
- unrelated lab architecture decisions

## Operating Rules

- Treat the live filesystem as the source of truth.
- Prefer inspecting current directories and files over relying on old notes.
- Do not rename, move, or delete library content in bulk without first recording intent and rollback notes.
- Keep notes at this directory root concise and operational.
- If mount or export behavior looks wrong, verify from the host before changing library content.

## Start Here

Read in this order:
1. `README.md`
2. `HANDOFF.md`
3. `MEMORY.md`
4. `MISSING_ISSUES.md`

## Current Working Context

- This library root lives at `/mnt/fearless/LIBRARY`.
- Current visible publisher directories include:
  - `Archie Comics`
  - `Dark Horse Comics`
  - `Rebellion`
- Existing work products already here:
  - `FOUND_FILES/`
  - `MISSING_ISSUES.md`

## Session Goal

A fresh Codex session here should quickly understand:
- what this directory is
- what files to read first
- what is currently known
- what should happen next
