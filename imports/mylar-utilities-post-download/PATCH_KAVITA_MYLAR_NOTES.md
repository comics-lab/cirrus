# Patch Notes: Kavita/Mylar Structure Tune-up

Generated: 2026-02-17 19:34:12 PST

## Proposed Mylar Config Patch (not yet applied)
Current:
- `folder_format = $Publisher/$Series $Type ($Year)`
- `file_format = $Series $VolumeN $Annual #$Issue ($monthname $Year)`

Proposed:
- `folder_format = $Publisher/$Series ($Year)`
- `file_format = $Series $VolumeN #$Issue`

## Why
- Keeps stable publisher/series organization.
- Reduces filename parser noise for Kavita and related tooling.
- Preserves richer metadata inside `ComicInfo.xml` rather than filename text.

## Operational Guardrails
- Keep `ComicInfo.xml` in archive root only.
- Continue treating `series.json` / `cvinfo` as pipeline metadata.
- If scanner noise appears, isolate operational sidecars from reader-only scan roots.

## Rollback
If needed, revert to prior format lines in `config.ini` and run:
1. Recheck Files (series or batch)
2. Rename Files
3. Library rescan in Kavita

