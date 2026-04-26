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

### Arthur agent

Responsible for:

- scanning source trees
- building and maintaining a searchable index
- searching for gaps listed in `../MISSING_ISSUES.md`
- staging confirmed matches into `FOUND_FILES/`
- updating `HANDOFF.md`
- recording context in `DIALOG.md`

### Sarah agentu

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

## Starting Prompt

Read and follow these files first, in this order:

1. `../AGENTS.md`
2. `../README.md`
3. `../HANDOFF.md`
4. `../MEMORY.md`
5. `../MISSING_ISSUES.md`
6. `FOUND_FILES/AGENTS.md`
7. `FOUND_FILES/README.md`
8. `FOUND_FILES/HANDOFF.md`
9. `FOUND_FILES/DIALOG.md`

You are operating on `reality.local` inside `/mnt/fearless/LIBRARY`.

Treat the root library files as the workspace-level instructions.
Treat the `FOUND_FILES` files as the missing-issue recovery sub-workflow.

Your role is the search and staging side of a two-host workflow:
- `reality.local` finds missing issues and stages them
- `cirrus` imports them into Mylar, rescans, renames, and closes gaps

Your immediate job is:

1. build or verify a searchable index of the available files under `/mnt/fearless/LIBRARY`
2. use `MISSING_ISSUES.md` as the active demand list
3. search for confirmed matches to the currently missing issues
4. stage confirmed matches into `FOUND_FILES/`
5. update `FOUND_FILES/HANDOFF.md` with structured entries for anything staged
6. update `FOUND_FILES/DIALOG.md` with useful search heuristics, false positives, and source-tree observations

Rules:
- prefer `.cbz`
- preserve original filenames unless disambiguation is necessary
- do not dump random files into `FOUND_FILES`
- only stage files that are `confirmed`, or clearly mark them `likely` / `possible`
- if a title has no match, record the negative result in `DIALOG.md`
- if duplicates exist, prefer the best-quality copy and explain why
- do not try to import into Mylar from `reality.local`
- do not modify `MISSING_ISSUES.md` unless explicitly instructed

Current priority is to search for the missing issues already listed in `MISSING_ISSUES.md`.

When you finish the first pass, report:
- what index you built or reused
- which missing issues were found
- which were not found
- what was staged into `FOUND_FILES`
- what heuristics or naming conventions were learned
