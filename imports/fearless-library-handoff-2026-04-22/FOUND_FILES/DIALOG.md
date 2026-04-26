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

### 2026-04-22 Arthur

- User designated the `reality.local` search/index agent as `Arthur`.
- Arthur's primary standing duty is to index and search for requested issues when Sarah asks for them.
- Library scale note: roughly 2 million comic-book files may exist across the drives on this system, so filesystem-native search tools should be used aggressively.
- Preferred available tools include `find`, `locate`, and similar host tools already present; if additional indexing or dedupe tools are needed, ask before adding them.
- Keep logs because the human operators want durable memory outside the current session.
- If Sarah is not actively working, Arthur may also use Sarah-authored scripts to convert `.cbr` archives to `.cbz`.
- Every `.cbz` file is expected to contain an embedded `ComicInfo.xml`.
- Sarah can provide additional process details when Arthur is ready for the Archie batch workflow.
- Current batch note from user: Sarah's present files are all from publisher `Archie Comics`.
- Duplicate-management and slack-space strategy are not yet settled; use this file heavily to record heuristics, tradeoffs, and open questions.
- When direction is unclear, communicate with the user or with Sarah rather than making quiet assumptions.

### 2026-04-22 reality.local

- Searched for a possible `Black Hood Comics #15` candidate outside the live library and found matching source files under `/mnt/phoenix/media/incoming/fearless-ssh/DOWNLOADS/Various/Archie/`.
- Best candidate staged to `FOUND_FILES`: `Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr`.
- Matching sibling copy exists in a duplicate download directory with `–(1)` suffix; preferred the original directory path for provenance clarity.
- Validation heuristic: `unrar` listing showed a readable 52-image archive with filenames `BlHo1501.jpg` through `BlHo1568.jpg`, including two `*.fiche.jpg` pages, which is consistent with a fiche-sourced Golden Age scan.
- Confidence remains `likely` rather than `confirmed` because no `ComicInfo.xml` was present and archive-level inspection did not verify cover branding beyond the filename and container context.

### 2026-04-22 Arthur

- First-pass live check of `/mnt/fearless/LIBRARY/Archie Comics/Archie (1960)` confirms the local series folder has gaps at `#151`, `#191`, `#237`, `#261`, `#266`, `#269`, and `#489`.
- Neighbor checks in the live series folder show adjacent issues present: `#150/#152`, `#190/#192`, `#236/#238`, `#260/#262`, `#265/#267/#268/#270`, and `#488/#490`.
- Targeted filename searches across `/mnt/fearless` and `/mnt/grackle` for exact `Archie (1960)` issue numbers did not find alternate copies of the missing issues.
- A broad issue-number search did return false positives in `The Adventures of Little Archie (1959)`, including `#151`; issue-number-only searching is not sufficient for Archie-family titles.
- Working heuristic: require both the series name `Archie` and either the series folder `Archie (1960)` or an exact filename pattern before treating a hit as relevant.

### 2026-04-22 Arthur

- Validated `FOUND_FILES/Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr` as a readable RAR v4 archive containing 52 JPEG pages named `BlHo1501` through `BlHo1568`.
- User visually confirmed the staged file's cover is `Black Hood Comics #15`, which is enough to promote the match from `likely` to `confirmed`.
- Built `FOUND_FILES/Black Hood Comics #015 (July 1945).cbz` from the staged CBR and embedded a minimal `ComicInfo.xml`.
- Local adjacent issues `#14` and `#16` already contain ComicInfo metadata and bracket issue `#15` between March 1945 and September 1945; the CBZ metadata currently uses `July 1945` as an inferred cover date pending Sarah or ComicVine verification.
- Keep both the original CBR and the converted CBZ for now so Cirrus has a reversible intake path.

### 2026-04-22 Arthur

- Standing rule from user: for Mylar work, Comic Vine is the absolute source of truth.
- When local filenames, scan dates, or neighboring-issue inference conflict with Comic Vine, use Comic Vine metadata for Mylar-facing naming and ComicInfo fields.

### 2026-04-22 Arthur

- User refinement: GCD data and Metron are also authoritative metadata sources at the same level for issue identity and descriptive fields.
- Practical distinction: GCD and Metron may or may not include the Mylar-critical `CVDB` id.
- Standing Mylar rule from user: `CVDB` is always required for Mylar work.
- Therefore, any Mylar-facing metadata or reconciliation flow must include Comic Vine lookup or an already-known `CVDB` id even when GCD or Metron provide the other descriptive metadata.

### 2026-04-22 Arthur

- Exception class: some items will likely never receive a `CVDB` id.
- Typical examples are omnibus editions, gallery editions, hardcovers, trades, compiled entities, and magazines.
- For these non-Mylar items, if GCD or Metron provides enough metadata to build a valid `ComicInfo.xml` or `MetronInfo.xml` that satisfies Kavita or Komga expectations, Arthur should create the metadata file(s), embed them into the archive, create the appropriate destination directories in the library tree, and then copy or move the files into that library location.
- Distinction to preserve: Mylar-facing periodical workflows still require `CVDB`; Kavita/Komga library-ingest workflows may proceed without `CVDB` when the item class is outside practical Mylar coverage and GCD/Metron metadata is sufficient.

### 2026-04-22 Arthur

- Rescan after user added `Archie 001-666 + Annuals 01-26 (1942-2015)` under `/mnt/fearless/LIBRARY/Archie Comics/` found all currently missing `Archie (1960)` gap issues present in the new source folder.
- Matching source files:
- `Archie 151 (1964-12) (c2c) (Mad Doctor Doom).cbr`
- `Archie 191 (1969) (Digital) (Shadowcat-Empire).cbz`
- `Archie 237 (1974) (Digital) (Asgard-Empire).cbr`
- `Archie 261 (1977) (Digital) (Shadowcat-Empire).cbz`
- `Archie 266 (1977) (Digital) (Shadowcat-Empire).cbz`
- `Archie 269 (1978) (Digital) (Shadowcat-Empire).cbz`
- `Archie 489 (1999) (Digital-SD) (Asgard-Empire).cbr`
- Neighbor checks in the same source folder also align with the live gap boundaries for `150/151/152`, `190/191/192`, `236/237/238`, `260/261/262`, `265/266/267/268/269/270`, and `488/489/490`.

### 2026-04-22 Arthur

- Comic Vine API key was found in `~/Projects/comicvine/comicvine-api.txt` and used for direct issue lookup.
- Verified Mylar-critical CVDB ids for the missing `Archie (1960)` issues:
- `151 -> CVDB85745`
- `191 -> CVDB85785`
- `237 -> CVDB85830`
- `261 -> CVDB85854`
- `266 -> CVDB85859`
- `269 -> CVDB85862`
- `489 -> CVDB151105`
- First-pass staging from the torrent folder worked, but several source archives extracted with warnings.
- Additional search under `/mnt/data/NAS_ROOT/Ignore for Now/_Older_Pubs/A/Archie/` found cleaner alternates for `#191`, `#237`, `#261`, `#266`, and `#269`.
- Those five staged CBZ files were rebuilt from the cleaner NAS alternates and now carry improved page counts:
- `#191` -> `37` images
- `#237` -> `36` images
- `#261` -> `36` images
- `#266` -> `36` images
- `#269` -> `37` images
- `#151` remains staged from the original Mad Doctor Doom source with a 7-Zip warning but a full-looking `37`-image set; no cleaner alternate has been identified yet.
- `#489` remains staged from an Asgard source recovered with one checksum-warning page; the NAS alternate found so far appears to be the same source rather than a cleaner replacement.

### 2026-04-22 Arthur

- Began staging the active `Archie (1960)` gaps after narrowing the search to the likely source tree `/mnt/phoenix/media/incoming/fearless-ssh/DOWNLOADS/Various/Archie/`.
- High-value source bundle found: `Archie 001-666 + Annuals 01-26 (1942-2015)`.
- Exact source hits found and staged for all remaining listed Archie gaps: `151`, `191`, `237`, `261`, `266`, `269`, and `489`.
- Staged formats are mixed: `191`, `261`, `266`, and `269` are already `.cbz`; `151`, `237`, and `489` are `.cbr`.
- Search heuristic refined: bundle-level naming can be more useful than library-folder-only checks; for Archie-family titles, require both the main-title series name and the issue number inside a source set clearly scoped to the main series.

### 2026-04-22 Arthur

- Cleaned `FOUND_FILES/` after rebuilding the preferred Archie intake set.
- Removed superseded raw-source Archie staging files so the directory now matches the normalized CBZ entries listed in `HANDOFF.md`.
- Intentional exception preserved: both `Black Hood Comics 15 paper 2fiche c2c re edit Jon.cbr` and `Black Hood Comics #015 (July 1945).cbz` remain staged to keep a reversible intake path for that issue.

### 2026-04-22 Arthur

- Re-scanned every staged `.cbz` in `FOUND_FILES/` and confirmed that each archive contains an embedded `ComicInfo.xml`.
- Verified embedded `CVDB` annotations for the preferred intake set:
- `Archie #151` -> `CVDB85745`
- `Archie #191` -> `CVDB85785`
- `Archie #237` -> `CVDB85830`
- `Archie #261` -> `CVDB85854`
- `Archie #266` -> `CVDB85859`
- `Archie #269` -> `CVDB85862`
- `Archie #489` -> `CVDB151105`
- `Black Hood Comics #015` -> `CVDB192106`
- Practical intake rule refinement: the normalized CBZ files are the Mylar-facing artifacts; retained source CBRs should be treated as fallback/recovery material unless a rebuild is needed.

### 2026-04-22 cirrus

- Confirmed runtime host identity with `hostname`: `cirrus`.
- Preferred intake CBZ files were copied from `FOUND_FILES/` into the live series folders:
- `Archie Comics/Archie (1960)`: `#151`, `#191`, `#237`, `#261`, `#266`, `#269`, `#489`
- `Archie Comics/Black Hood Comics (1943)`: `#015`
- Local Mylar working tree identified at `/home/rmleonard/Projects/mylar-library/`.
- Live Mylar DB path identified as `/home/rmleonard/Projects/mylar-library/mylar.db`.
- DB snapshot at this point:
- `Archie (1960)` / ComicID `9628` shows `Have/Total = 553/553`; target issues are already `Downloaded` in the DB, but some `Location` fields still point at older `.cbr` names.
- `Black Hood Comics (1943)` / ComicID `19398` still shows `Have/Total = 10/11`; issue `15` remains `Wanted` in the DB before rescan.
- Mylar control endpoint expected from config: `http://127.0.0.1:8690/library/` or `http://192.168.1.126:8690/library/` with API enabled.
- Blocker observed: both endpoint checks failed with connection errors, and no active Mylar process was visible; existing `library.pid` appears stale.
- Intended next Sarah step was: start Mylar, run `recheckFiles` for ComicIDs `9628` and `19398`, then `manualRename`, then verify updated `Have/Total` and remove resolved gaps from `../MISSING_ISSUES.md`.
- User interrupted the service-start attempt due to network issues before completion. No Mylar-side mutation was confirmed after file placement.
