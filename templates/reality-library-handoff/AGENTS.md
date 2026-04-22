# AGENTS.md — FOUND_FILES Workspace

This workspace exists to coordinate missing-issue recovery between
`reality.local` and `cirrus`.

## Scope

Use this directory only for:

- finding files that satisfy known missing-issue gaps
- staging confirmed files for Cirrus pickup
- documenting provenance and confidence
- sharing concise state between agents

Do not use this directory as:

- a general download bucket
- a scratch space for unrelated experiments
- a duplicate archive dump
- a replacement for the real library

## Source of Truth

The active missing-issue list is:

- `../MISSING_ISSUES.md`

That file is the demand signal.

This directory is the supply handoff.

## Roles

### reality.local agent

Responsible for:

- scanning source trees
- building and maintaining a searchable index
- searching for gaps listed in `../MISSING_ISSUES.md`
- staging confirmed matches into `FOUND_FILES/`
- updating `HANDOFF.md`
- recording context in `DIALOG.md`

### cirrus agent

Responsible for:

- validating staged files
- importing them into the correct Mylar-managed series folders
- running Mylar rescan and rename actions
- confirming issue counts in Mylar
- updating `../MISSING_ISSUES.md` when a gap is resolved
- recording outcomes in `DIALOG.md`

## File Handling Rules

- prefer `.cbz`
- keep original filenames unless a rename is needed to disambiguate
- do not delete staged files silently
- if you replace a staged file with a better copy, record why in `HANDOFF.md`
- if two files appear to match the same issue, keep both only if the reason is
  documented

## Confidence Rules

- `confirmed`: safe for Cirrus to import
- `likely`: needs manual validation before import
- `possible`: weak candidate, keep only if nothing better exists

## Communication Rules

Use:

- `HANDOFF.md` for structured, action-oriented state
- `DIALOG.md` for freeform reasoning, discoveries, caveats, and lessons learned

Keep both concise, factual, and current.

## Operational Bias

Prefer:

- explicit provenance
- shallow directory structure
- one issue, one staged file
- reversible actions

Avoid:

- hidden assumptions
- large unexplained dumps
- unstated confidence
- “I think this is right” without evidence
