# Intake Flow Diagram

This is the end-to-end Cirrus comic intake path, from download to the Mylar staging basket.

The penultimate landing zone is:

- `/mnt/phoenix/media/incoming/mylar-import`

Mylar then watches the container path:

- `/mylar-imports`

```mermaid
flowchart TD
    A[JDownloader / torrent download lands in<br/>/mnt/phoenix/media/incoming/jdownloader] --> B[Extract zip payloads<br/>utilities/extract_zip_payloads.py]
    A --> C[Convert .cbr to .cbz<br/>utilities/cbr_to_cbz.py]

    B --> B1[Failure lane<br/>zip corrupt / no payloads / webp-only / already expanded]
    C --> C1[Failure lane<br/>unsupported archive method / corrupt archive / no space / verify failed]

    B --> D[Resulting archives in intake tree]
    C --> D

    D --> E[Audit structural readiness<br/>utilities/cbz_audit.py]
    E --> E1[Failure lane<br/>bad zip / missing ComicInfo.xml / missing Series or Number / no ComicVine ref]

    E --> F[Pre-pass normalization<br/>utilities/prepass_normalize.py]
    F --> F1[Inputs:<br/>series.json<br/>root ComicInfo.xml<br/>local CBL cache<br/>seeded series cache]
    F --> F2[Writes or refreshes:<br/>ComicInfo.xml<br/>MetronInfo.xml<br/>publisher/series folder placement]
    F --> F3[Failure lane<br/>no strong local match / ambiguous issue / manual review]

    F --> G[Pass 1 metadata write<br/>utilities/pass1_write_comicinfo.py]
    G --> G1[Inputs:<br/>ComicVine API + local resolver cache + ComicInfo.xml + series.json + CBL cache]
    G --> G2[Populates or updates:<br/>Series<br/>Number<br/>Year<br/>Publisher<br/>Volume<br/>Notes<br/>Web<br/>ComicVine issue id]
    G --> G3[Failure lane<br/>candidate / unresolved / API error / weak match]

    G --> H[Promote Mylar-valid archives<br/>utilities/promote_mylar_import.py]
    H --> H1[Moves only files that pass audit]
    H --> H2[/mnt/phoenix/media/incoming/mylar-import]
    H --> H3[Failure lane<br/>not_mylar_valid / skipped_webp]

    H2 --> I[Mylar container consumes the staged file<br/>/mylar-imports]
    I --> J[Library placement / post-processing]

    K[Optional paced path<br/>utilities/mylar_paced_import.py] --> K1[Stages one file at a time into Mylar queue]
    K1 --> K2[Reject lane<br/>/mnt/phoenix/media/incoming/mylar-import/paced-rejects]
```

## Source To Field Map

The scripts currently draw from these sources:

- `ComicInfo.xml`
- `MetronInfo.xml`
- `series.json`
- local CBL SQLite cache
- local GCD-derived metadata cache
- ComicVine API
- ISBN / catalog metadata for library-oriented books
- file names and folder names

What each source contributes:

- `ComicInfo.xml`
  - series name
  - issue number
  - year
  - publisher
  - notes
  - web link

- `MetronInfo.xml`
  - ComicVine series id
  - ComicVine issue id
  - archive-side library metadata

- `series.json`
  - trusted ComicVine volume id
  - series name
  - volume
  - start year
  - book type / imprint hints

- local CBL cache
  - ComicVine series id
  - ComicVine issue id
  - issue lookup hints from reading lists

- local GCD metadata cache
  - series title
  - issue title
  - publisher
  - year
  - descriptive bibliographic data

- ComicVine API
  - ComicVine issue id
  - ComicVine series id
  - final resolver confirmation

- ISBN / catalog metadata
  - ISBN
  - title
  - publisher
  - publication year
  - library-only metadata for books that will not have ComicVine ids

- file and folder names
  - title normalization
  - volume inference
  - issue number inference
  - special / annual / omnibus / trade indicators

## Failure Side Lanes

Each stage should leave failures in a clearly named side directory instead of silently dropping them:

- zip extraction failures
  - archive / no payload / manual inspection

- cbr conversion failures
  - raw archive repair / quarantine / re-download

- audit failures
  - missing metadata / bad zip / not yet Mylar-valid

- pre-pass failures
  - manual review / ambiguous match

- Pass 1 failures
  - candidate / unresolved / API issue

- promotion failures
  - not Mylar-valid / skipped WebP / duplicate target

- paced import failures
  - paced rejects under `paced-rejects`

## Final State

The file should end up in:

- `/mnt/phoenix/media/incoming/mylar-import`

and then be consumed by Mylar from:

- `/mylar-imports`

