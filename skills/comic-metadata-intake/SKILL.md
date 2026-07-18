---
name: comic-metadata-intake
description: Parse, enrich, validate, and stage digital comic archives for Mylar and Kavita using local metadata first, explicit provenance, confidence scoring, and rate-limited remote lookup.
---

# Comic Metadata Intake

Use this skill when working on CBZ intake, ComicInfo.xml/MetronInfo.xml creation, CBL/GCD/Metron/ComicVine matching, Mylar promotion, or Kavita library readiness.

Read `docs/comic-metadata-intake-contract.md` before changing parser behavior. Read
`docs/intake-to-mylar-workflow.md` when operating the full pipeline.

## Operating Rules

1. Preserve the original filename, path, and hash before changing an archive.
2. Inspect local embedded XML, `series.json`, `cvinfo`, GCD, ISBN, Metron, and CBL data before using ComicVine.
3. Treat filename parsing as a hint, never as authoritative identity.
4. Resolve edition type explicitly. A hardcover, trade, omnibus, annual, and regular issue are not interchangeable.
5. Record field-level provenance and competing candidates in the report.
6. Keep remote ComicVine requests sequential, cached, and throttled. Local archive inspection may be parallelized.
7. Validate XML after writing and validate the CBZ as a ZIP before promotion.
8. Separate `kavita_ready` from `mylar_ready`; do not force non-CV editions into Mylar's automated basket.
9. Use a dry-run report before any rename, move, or overwrite. Apply only the saved approved plan.
10. Never edit CBL source files or the canonical cache automatically to resolve an ambiguity.

## Preferred Pipeline

Use the existing utilities as stages, but keep their responsibilities distinct:

- inspect and audit the CBZ
- normalize local metadata and consult the cache
- resolve missing or conflicting identity
- materialize both XML files and sidecars
- build the Mylar-shaped directory and filename
- audit again
- promote only approved `mylar_ready` records
- let Mylar import, then recheck and verify the resulting library path

The next implementation improvement should be a machine-readable resolution record between
the resolver and materializer. It prevents each stage from reparsing the same archive and
makes retries cheap.

## Failure Handling

Do not delete failed inputs. Place them in a named review/error lane with a report reason.
Common causes are corrupt ZIPs, nested metadata, ambiguous series/year, edition-type mismatch,
duplicate destination, malformed XML, and missing ComicVine representation.

## Output Standard

For every staged archive, produce:

- valid root `ComicInfo.xml`
- valid root `MetronInfo.xml`
- normalized path/name based on the current Mylar config
- provenance and disposition in CSV/JSON
- preserved original filename in notes or sidecar data
