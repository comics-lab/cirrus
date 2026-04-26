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

### 2026-04-22

- `series`: `Archie (1960)`
- `issue`: `151`
- `comicid`: `9628`
- `filename`: `Archie #151 (December 1964).cbz`
- `source_path`: `/mnt/fearless/LIBRARY/Archie Comics/Archie 001-666 + Annuals 01-26 (1942-2015)/Archie 151 (1964-12) (c2c) (Mad Doctor Doom).cbr`
- `staged_path`: `FOUND_FILES/Archie #151 (December 1964).cbz`
- `confidence`: `confirmed`
- `notes`: `Embedded ComicInfo.xml includes CVDB85745 and Comic Vine metadata. Source archive extracted with 7-Zip warning but yielded a full 37-image set matching the archive listing. Cleaner alternate not yet identified.`

- `series`: `Archie (1960)`
- `issue`: `191`
- `comicid`: `9628`
- `filename`: `Archie #191 (June 1969).cbz`
- `source_path`: `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/Archie (2014)/{1942+ ...} Archie/{1942-2015} Archie Comics 001 - 666 (Collection) (1942-2015)/Archie Comics 101-200/Archie 191 (1969-06) (c2c) (Mad Doctor Doom).cbr`
- `staged_path`: `FOUND_FILES/Archie #191 (June 1969).cbz`
- `confidence`: `confirmed`
- `notes`: `Rebuilt from a cleaner alternate source after the initial Shadowcat torrent copy extracted with CRC warnings and only 28 images. Embedded ComicInfo.xml includes CVDB85785. Final staged file contains 37 images plus ComicInfo.xml.`

- `series`: `Archie (1960)`
- `issue`: `237`
- `comicid`: `9628`
- `filename`: `Archie #237 (August 1974).cbz`
- `source_path`: `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/Archie (2014)/{1942+ ...} Archie/{1942-2015} Archie Comics 001 - 666 (Collection) (1942-2015)/Archie Comics 201-300/Archie 237 (1974) (c2c) (Jojo).cbr`
- `staged_path`: `FOUND_FILES/Archie #237 (August 1974).cbz`
- `confidence`: `confirmed`
- `notes`: `Rebuilt from a cleaner alternate source after the initial Asgard torrent copy needed recovery. Embedded ComicInfo.xml includes CVDB85830. Final staged file contains 36 images plus ComicInfo.xml.`

- `series`: `Archie (1960)`
- `issue`: `261`
- `comicid`: `9628`
- `filename`: `Archie #261 (April 1977).cbz`
- `source_path`: `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/Archie (2014)/{1942+ ...} Archie/{1942-2015} Archie Comics 001 - 666 (Collection) (1942-2015)/Archie Comics 201-300/Archie 261 (1977) (GIT+edit).cbz`
- `staged_path`: `FOUND_FILES/Archie #261 (April 1977).cbz`
- `confidence`: `confirmed`
- `notes`: `Rebuilt from a cleaner alternate GIT+edit source after the initial Shadowcat torrent copy extracted with warnings and only 25 images. Embedded ComicInfo.xml includes CVDB85854. Final staged file contains 36 images plus ComicInfo.xml.`

- `series`: `Archie (1960)`
- `issue`: `266`
- `comicid`: `9628`
- `filename`: `Archie #266 (November 1977).cbz`
- `source_path`: `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/Archie (2014)/{1942+ ...} Archie/{1942-2015} Archie Comics 001 - 666 (Collection) (1942-2015)/Archie Comics 201-300/Archie 266 (1977) (GIT+edit).cbz`
- `staged_path`: `FOUND_FILES/Archie #266 (November 1977).cbz`
- `confidence`: `confirmed`
- `notes`: `Rebuilt from a cleaner alternate GIT+edit source after the initial Shadowcat torrent copy extracted with warnings and only 25 images. Embedded ComicInfo.xml includes CVDB85859. Final staged file contains 36 images plus ComicInfo.xml.`

- `series`: `Archie (1960)`
- `issue`: `269`
- `comicid`: `9628`
- `filename`: `Archie #269 (March 1978).cbz`
- `source_path`: `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/Archie (2014)/{1942+ ...} Archie/{1942-2015} Archie Comics 001 - 666 (Collection) (1942-2015)/Archie Comics 201-300/Archie 269 (1978) (c2c) (Jojo).cbr`
- `staged_path`: `FOUND_FILES/Archie #269 (March 1978).cbz`
- `confidence`: `confirmed`
- `notes`: `Rebuilt from a cleaner alternate source after the initial Shadowcat torrent copy extracted with warnings and only 25 images. Embedded ComicInfo.xml includes CVDB85862. Final staged file contains 37 images plus ComicInfo.xml.`

- `series`: `Archie (1960)`
- `issue`: `489`
- `comicid`: `9628`
- `filename`: `Archie #489 (November 1999).cbz`
- `source_path`: `/mnt/fearless/LIBRARY/Archie Comics/Archie 001-666 + Annuals 01-26 (1942-2015)/Archie 489 (1999) (Digital-SD) (Asgard-Empire).cbr`
- `staged_path`: `FOUND_FILES/Archie #489 (November 1999).cbz`
- `confidence`: `confirmed`
- `notes`: `Embedded ComicInfo.xml includes CVDB151105 and Comic Vine metadata. Staged file was rebuilt via unrar recovery after one checksum-warning page in the source archive; final staged file contains 25 images plus ComicInfo.xml. Alternate NAS copy found so far appears to be the same Asgard source rather than a cleaner replacement.`

- `series`: `Black Hood Comics (1943)`
- `issue`: `15`
- `comicid`: `19398`
- `filename`: `Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr`
- `source_path`: `/mnt/phoenix/media/incoming/fearless-ssh/DOWNLOADS/Various/Archie/Special Comics   Hangman Comics   Black Hood Comics #1 - 19 (1942-1946) –/Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr`
- `staged_path`: `FOUND_FILES/Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr`
- `confidence`: `confirmed`
- `notes`: `User visually confirmed the cover as Black Hood Comics #15. Arthur validated the staged CBR as a readable 52-image archive, then built a sibling CBZ with embedded ComicInfo.xml for Cirrus intake. This CBR is retained only as a reversible source/fallback artifact; preferred Mylar intake is the sibling CBZ. Duplicate source also exists in the sibling –(1) download folder; staged the non-duplicate path.`

- `series`: `Black Hood Comics (1943)`
- `issue`: `15`
- `comicid`: `19398`
- `filename`: `Black Hood Comics #015 (July 1945).cbz`
- `source_path`: `FOUND_FILES/Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr`
- `staged_path`: `FOUND_FILES/Black Hood Comics #015 (July 1945).cbz`
- `confidence`: `confirmed`
- `notes`: `Converted from the staged CBR on 2026-04-22. Preferred intake artifact. Embedded ComicInfo.xml was rechecked on 2026-04-22 and contains CVDB192106 plus verified metadata from Comic Vine and local series context: Title=The Case of the Blood-Red Rubies, Series=Black Hood Comics, Number=15, Volume=1943, Year=1945, Month=07, Day=01, Publisher=Archie Comics, Web=https://comicvine.gamespot.com/black-hood-comics-15-the-case-of-the-blood-red-rubies/4000-192106/, PageCount=52. Cover confirmation came from user.`

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
- Cirrus-side placement into the live library folders was completed on `2026-04-22`, but Mylar verification did not complete because the local Mylar service/API was unreachable at the time of validation.
- As of the last DB check, `Archie (1960)` already showed `553/553` in Mylar, while `Black Hood Comics (1943)` still showed `10/11` with issue `15` `Wanted` pending rescan.
