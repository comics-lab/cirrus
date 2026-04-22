# FOUND_FILES Handoff

Use this file to hand work from `reality.local` to `cirrus`.

Update it every time files are staged in this directory.

## Current Goal

Search local source trees for issues listed in:

- `../MISSING_ISSUES.md`

and place confirmed matches in:

- `FOUND_FILES/`

## Required Entry Format

For each staged file, record:

- `series`
- `issue`
- `comicid` if known
- `filename`
- `source_path`
- `staged_path`
- `confidence`
- `notes`

## Entries

### Example

- `series`: `Archie`
- `issue`: `151`
- `comicid`: `9628`
- `filename`: `Archie #151 (August 1964).cbz`
- `source_path`: `/some/source/tree/Archie #151.cbz`
- `staged_path`: `FOUND_FILES/Archie #151 (August 1964).cbz`
- `confidence`: `confirmed`
- `notes`: `Filename and issue count match Mylar gap list.`

## Cirrus Intake Rule

When Cirrus consumes a staged file, it should:

1. verify the issue really matches the intended series and issue number
2. place it into the existing Mylar series folder
3. run Mylar:
   - `recheckFiles`
   - `manualRename`
4. verify Mylar `Have / Total` changed as expected
5. then mark the item completed below

## Completed

- none yet

## Notes

- If a file is only `likely` or `possible`, say why.
- If multiple files satisfy the same gap, note which one is preferred and why.
- If a search failed for a given gap, record that too. Negative search results
  are useful and prevent repeated wasted work.
