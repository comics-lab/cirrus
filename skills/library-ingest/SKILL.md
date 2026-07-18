---
name: library-ingest
description: Discover, enrich, tag, validate, and construct a reversible comic-library ingest tree from mixed sources.
---

# Library Ingest

Use this skill for source discovery, collection inventory, metadata enrichment, tagging,
directory construction, duplicate analysis, or library integrity checks. For detailed CBZ
identity resolution and Mylar promotion, also load `comic-metadata-intake` and its contract.

## Workflow

1. Map source roots, metadata providers, and destination layout.
2. Capture hashes and original paths before changes.
3. Validate naming and tagging rules with a dry-run report.
4. Apply changes in reversible stages.
5. Re-audit archives, metadata, duplicates, and destination collisions.
6. Document outcomes, rejected records, and rollback guidance.

## Deliverables

- Inventory or ingest report
- Approved transformation or promotion plan
- Validated metadata and file layout
- Error/review queues with reasons
- Runbook or decision update when the workflow changes

## Guardrails

- Do not perform destructive bulk changes without explicit approval.
- Preserve metadata provenance and original filenames.
- Keep source archives, staging, curated library, and service state separate.
- Do not treat a successful file move as proof of Mylar acceptance.
