# Comic Metadata Intake Contract

This contract defines what the Cirrus comic parser must produce before an archive is
sent toward Mylar or the curated library. It is intentionally separate from any one
agent, API, or parser implementation.

## Processing States

Each CBZ has one disposition:

- `invalid_archive`: unreadable ZIP, zero length, no comic pages, or duplicate target
- `metadata_review`: metadata is incomplete, conflicting, or below the confidence threshold
- `kavita_ready`: readable and tagged for library use, but not safe for automated Mylar import
- `mylar_ready`: readable, rooted metadata is valid, and the Mylar identity is sufficiently
  strong for the configured import path
- `imported`: Mylar accepted it and the post-import verification succeeded

`kavita_ready` must never be silently upgraded to `mylar_ready` merely because a filename
looks plausible.

## Required Per-Archive Record

The parser report should contain at least:

- archive path and SHA-256
- original filename and normalized filename
- publisher, series, volume, issue/edition number, title, year, and cover date
- edition type: `issue`, `annual`, `trade`, `graphic_novel`, `omnibus`, `hardcover`, or `unknown`
- ComicVine series/issue ids when known
- Metron id, GCD id, ISBN, LoCG id, and other identifiers when known
- source and confidence for each chosen field
- conflicts and rejected candidates
- ComicInfo/MetronInfo parse and write status
- final disposition and reason

Provenance belongs in the report and in archive metadata where possible. The original
filename must not be lost during renaming.

## Source Precedence

Use sources in this order, field by field:

1. explicit human correction or trusted existing embedded metadata
2. local GCD database and local sidecars (`series.json`, `cvinfo`)
3. CBL cache, only when the series/number/year identity is unambiguous
4. local ISBN/Metron cache or API
5. ComicVine API, rate-limited and cached
6. filename and directory heuristics as hints only

An identifier from a weaker source may support a match, but must not overwrite a stronger
source without recording the conflict.

## XML Requirements

Every `kavita_ready` or `mylar_ready` CBZ must contain valid root-level:

- `ComicInfo.xml`
- `MetronInfo.xml`

`ComicInfo.xml` should carry the normalized display fields and stable identifiers in the
format supported by the consumer. `MetronInfo.xml` should carry Metron/GCD/ISBN identifiers
when available and preserve ComicVine ids as cross-reference data, not as a fabricated
Metron identity. XML must be parsed again after writing.

## Matching Rules

The parser should score a candidate using identity components, not series and issue alone:

- normalized series
- publisher
- volume/start year
- issue number or edition type
- title/subtitle
- cover date
- stable identifiers

Series plus issue is never sufficient by itself when multiple years, volumes, or editions
exist. A single candidate with a strong local identifier can be accepted; conflicting
candidate identities must go to `metadata_review`.

## Mylar Handoff Rules

The buildout stage may create the Mylar-shaped publisher/series tree and normalized filename,
but promotion is a separate operation. Promotion requires:

- valid CBZ
- rooted, parseable ComicInfo.xml
- stable series identity
- issue or edition identity
- no unresolved identity conflict
- destination collision check

Mylar's live `folder_format`, `file_format`, and import settings are configuration inputs,
not hard-coded policy. The parser must record the template version or config path used.

## Safe Architecture

Keep the implementation split into four deterministic layers:

1. `inspect`: read archive, sidecars, local databases, and hashes without changing files
2. `resolve`: produce candidates, field provenance, conflicts, and confidence
3. `materialize`: write XML, sidecars, names, and directories only from an approved record
4. `promote`: copy or move an approved tree into Mylar's import basket

Remote API access belongs only in `resolve`, with a persistent cache, retry/backoff, and a
single request throttle. Re-running `materialize` or `promote` must be idempotent.

## Review Queue

The parser must retain rejected candidates and explain why an archive was not promoted. Useful
review reasons include:

- no readable pages
- missing series or edition identity
- conflicting CBL and GCD records
- ComicVine result below threshold
- multiple equally strong candidates
- ISBN/Metron-only edition not represented in ComicVine
- destination collision
- XML write or post-write validation failure
