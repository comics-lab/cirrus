# Comic Metadata Intake Agent Contract

## Purpose

Resolve comic identity and produce trustworthy metadata for Mylar and Kavita without treating
ComicVine as the only valid source.

## Inputs

- CBZ archive and SHA-256
- Embedded `ComicInfo.xml` and `MetronInfo.xml`
- Filename, directory, `series.json`, and `cvinfo`
- Local GCD, CBL, ISBN, and Metron data
- ComicVine API only when local evidence is insufficient

## Outputs

- Field-level metadata with source and confidence
- Candidate matches and conflicts
- Valid root `ComicInfo.xml` and `MetronInfo.xml`
- Normalized path/name based on the live Mylar configuration
- Disposition: `metadata_review`, `kavita_ready`, or `mylar_ready`
- JSON/CSV report retaining original filename and processing timestamp

## Resolution Rules

1. Prefer trusted existing metadata and human corrections.
2. Prefer local GCD and sidecars before CBL or remote APIs.
3. Use CBL only when series, edition, year, and issue identity are unambiguous.
4. Use ComicVine sequentially with persistent caching and backoff.
5. Treat series plus issue number as insufficient when multiple volumes or editions exist.
6. Treat ISBN/Metron/GCD-only editions as valid review or Kavita candidates even without a
   ComicVine id.

## Mutation Boundaries

- Inspection and resolution may run read-only.
- Materialization may write only from an approved resolution record.
- Promotion may move/copy only records explicitly marked `mylar_ready`.
- CBL source files and canonical cache rows are never corrected automatically.

## Validation

- [ ] Archive remains readable after metadata rewrite.
- [ ] Both XML files parse after writing.
- [ ] Provenance and conflicts are recorded.
- [ ] Edition type is identified or sent to review.
- [ ] Mylar promotion status is independent from Kavita readability.
