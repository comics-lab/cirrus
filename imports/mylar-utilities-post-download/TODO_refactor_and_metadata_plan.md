# TODO: Refactor + Metadata Integration Plan

Priority: High (foundational work)

## Phase 1 — Static Hygiene (low risk)
- Add linting (ruff/flake8) and basic formatting rules.
- Run dead-code scan (vulture) and produce a removal list.
- Identify cyclomatic hotspots and error-prone functions.
- Add minimal type hints in highest-churn paths (import, post-process, move, rename).

## Phase 2 — Architectural Mapping (low risk)
- Produce module dependency map (UI/WebIO/DataIO/Core).
- List cross-module violations (e.g., WebIO calling deep data internals).
- Define “bucket” boundaries and document interfaces.

## Phase 3 — Targeted Refactors (medium risk)
- Extract WebIO / DataIO / Core modules with thin adapters.
- Preserve behavior while reducing coupling.
- Add regression tests in critical paths (import/move/rename/scan).

## Metadata Integration (high priority)
- Integrate Grand Comics Database as a local datasource.
- Integrate Metron tools/API to populate metadata and correct series/issue naming.
- Define source precedence rules (ComicVine vs GCD vs Metron).
- Build a reconciliation workflow for naming conflicts.

## Cross-App Compatibility (high priority)
- Ensure naming conventions align across Mylar, Kavita, and (optionally) Komf.
- Verify series/issue/volume naming compatibility for Kavita imports.
- Define/validate filename templates compatible with all tools.

## Pre-Import Cleanup (high priority)
- Build a pre-import pass to normalize filenames, detect ambiguity, and pre-seed metadata.
- Output buckets: clean / needs review / broken.

## API Bridge Sync (high priority)
- Build an unattended bridge-sync script that iterates across all issues via Mylar DB/API, not only Wanted.
- For each issue, fetch/update metadata from ComicVine using `ComicID` + `IssueID` as primary keys.
- Implement rate-limit aware pacing (token bucket + jittered backoff) and a monitor file with heartbeat/progress.
- Keep continuous sweep mode ("paint the bridge"): start from first issue, run to end, then restart.
- Store checkpoints (last issue processed, retry counts, error buckets) for crash-safe resume.
