# Kavita vs Mylar3 Directory Structure (Comparison + Recommendations)

## Scope
This compares:
- **Kavita scanner expectations** (from official docs)
- **Current Mylar3 output** on this host
- Suggested adjustments to reduce scan ambiguity and duplicate/phantom entries

## Current Mylar3 Output (Observed)
From `config.ini`:
- `destination_dir = /mnt/grackle/LIBRARY`
- `folder_format = $Publisher/$Series $Type ($Year)`
- `file_format = $Series $VolumeN $Annual #$Issue ($monthname $Year)`
- `series_metadata_local = True`
- `cvinfo = True`

Observed example:
- `/mnt/grackle/LIBRARY/Marvel/The Amazing Spider-Man (2022)/The Amazing Spider-Man v6 #033 (November 2023).cbz`

## Kavita-Preferred Structure (Docs Summary)
Kavita documentation emphasizes:
1. Keep each Kavita library scoped to one media type (do not mix Comics/Manga/etc in one root).
2. Keep a clear series-per-folder layout.
3. Avoid scanner confusion from irregular nesting/adjacent-folder edge cases.
4. Use consistent archive metadata handling (`ComicInfo.xml` support; Mylar is a known metadata provider/integration path).

## Side-by-Side
| Area | Mylar3 current | Kavita preference | Impact |
|---|---|---|---|
| Library root | `/mnt/grackle/LIBRARY` | One root per media library in Kavita | Mixed content can increase false grouping |
| Publisher level | Includes publisher directory | Optional for Kavita | Usually fine; helps browsing |
| Series folder | `$Series $Type ($Year)` | Series folder per title | Good match |
| Filename verbosity | Includes volume, annual token, issue, month/year | Consistent issue naming; avoid over-complex patterns | Complex names can reduce parser reliability on edge cases |
| Sidecar metadata | `series.json`, `cvinfo` in dirs | Kavita mainly cares about comic files + `ComicInfo.xml` | Extra sidecars are fine but should not confuse scan paths |

## Recommended Changes

### 1) Keep current folder hierarchy (good baseline)
Current `Publisher/Series (Year)` style is compatible with Kavita and useful operationally.

### 2) Split Kavita libraries by media class
If not already separated, use distinct Kavita roots (Comics only under this root). This aligns with Kavita guidance and reduces cross-media scan errors.

### 3) Simplify file naming slightly (optional but recommended)
Consider reducing filename complexity to this Mylar pattern:
- `file_format = $Series $VolumeN #$Issue`

Rationale:
- Keeps deterministic matching for scanners
- Removes month text noise from filename parsing
- Metadata still retained in `ComicInfo.xml`

### 4) Keep `ComicInfo.xml` in archive root only
Continue enforcing root-level `ComicInfo.xml` (not nested inside archive subfolders). This is the most important metadata consistency rule for downstream tools.

### 5) Treat `series.json`/`cvinfo` as operational metadata, not reader metadata
Keep them for pipeline logic, but if Kavita scan behavior is noisy in any sub-tree, isolate these operational files from reader-only roots.

## Suggested “Kavita-Optimized” Mylar Profile
- `folder_format = $Publisher/$Series ($Year)`
- `file_format = $Series $VolumeN #$Issue`

This preserves publisher + series organization while keeping filenames scanner-friendly.

## References
- Kavita scanner docs: https://wiki.kavitareader.com/guides/scanner/
- Kavita file management docs: https://wiki.kavitareader.com/guides/managing-files/
- Kavita scanner/file handling notes: https://wiki.kavitareader.com/guides/scanner/managefiles/
- Kavita + Mylar integration page: https://wiki.kavitareader.com/guides/scanner/managefiles/mylar/
