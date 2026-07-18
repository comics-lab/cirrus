# Mylar v3 Buildout

This repo now has a separate v3-only buildout utility for staged intake trees:

- `utilities/mylar_v3_buildout.py`

Purpose:

- normalize staged CBZ branches toward the current Mylar naming templates
- add or refresh `ComicInfo.xml` and `MetronInfo.xml`
- write `series.json` and `cvinfo` sidecars when a ComicVine id is available
- preserve provenance by recording original filename and normalization time
- optionally copy or move the finished branch into `/mnt/phoenix/media/incoming/mylar-imports`

Current Mylar naming templates in live config:

- `folder_format = $Publisher/$Series $Type ($Year)`
- `file_format = $Series $VolumeN $Annual #$Issue ($monthname $Year)`

Recommended usage:

1. run in `--dry-run` mode first
2. inspect the report under `data/reports/`
3. rerun with `--promote`
4. add `--move` only when the source branch is ready to leave the buildout tree

The v3 utility is intentionally separate from the current intake pipeline so the
existing working path remains unchanged while the new naming convention is
stabilized.
