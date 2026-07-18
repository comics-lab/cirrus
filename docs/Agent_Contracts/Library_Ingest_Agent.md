# Library Ingest Agent Contract

## Purpose

Own discovery, metadata enrichment, tagging, and stable construction of the Cirrus comic
library while preserving provenance and reversibility.

## Inputs

- Source roots such as JDownloader, weekly lots, legacy libraries, or found-file queues
- Current naming and directory rules
- Existing CBZ archives and embedded metadata
- Local CBL, GCD, ISBN, Metron, and series caches

## Outputs

- A machine-readable inventory or resolution report
- Reversible file/layout changes from an approved plan
- Validated `ComicInfo.xml` and `MetronInfo.xml` where applicable
- Duplicate/error/review dispositions with reasons
- Updated runbook or decision note when behavior changes

## Guardrails

- Do not perform destructive bulk changes without explicit approval.
- Preserve original path, filename, hash, and metadata provenance.
- Treat filename heuristics as hints, not identity.
- Do not silently overwrite conflicting metadata or canonical CBL source data.
- Keep Kavita readiness separate from Mylar readiness.

## Validation

- [ ] Archives are readable ZIP/CBZ files with nonzero page content.
- [ ] XML is present at the archive root and parses after writing.
- [ ] Naming/layout policy is recorded and validated.
- [ ] Duplicate and collision checks completed.
- [ ] Report includes source, confidence, disposition, and rollback information.
