# FOUND_FILES Workspace

This directory is the handoff workspace between:

- the indexing/search agent on `reality.local`
- the import/reconciliation agent on `cirrus`

Its purpose is narrow and operational:

1. find files that satisfy known missing-issue gaps
2. stage those files in one predictable place
3. document what was found, from where, and why it matters
4. let Cirrus pick them up and move them into the Mylar/Kavita workflow

## What Belongs Here

- files that match entries in `../MISSING_ISSUES.md`
- notes about where they were found
- search/index status
- handoff instructions for Cirrus

## What Does Not Belong Here

- random intake or unsorted downloads
- annual/digest/special-format material unless explicitly requested
- speculative matches without notes
- duplicates without explanation

## Expected Workflow

1. `reality.local` indexes available source trees.
2. The search agent looks for items listed in `../MISSING_ISSUES.md`.
3. Confirmed matches are copied or moved into `FOUND_FILES/`.
4. `HANDOFF.md` is updated with:
   - series
   - issue number
   - source path
   - confidence
   - any caveats
5. Cirrus imports the staged file into the correct Mylar-managed series folder.
6. Cirrus runs:
   - `recheckFiles`
   - `manualRename`
   - and any later metatag step if needed
7. Once confirmed, the issue is removed from `../MISSING_ISSUES.md`.

## Directory Expectations

Keep this directory simple.

- one staged file per missing issue, when possible
- no nested archive trees unless needed for provenance
- if multiple candidate files exist for the same issue, keep them in a
  subdirectory named for the series and document the reason in `HANDOFF.md`

## Confidence Labels

Use one of these in `HANDOFF.md`:

- `confirmed`
- `likely`
- `possible`

Only `confirmed` files should be assumed safe for immediate Cirrus import.

## Operating Principle

This is a coordination directory, not a library.
Keep it small, explicit, and easy to audit.
