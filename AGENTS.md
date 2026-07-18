# AGENTS.md — Cirrus

This repo documents and manages the `cirrus` host and its comic-library intake services.

## Scope

This is a machine- and operations-scoped repo, not an org-wide policy repo.

Use this repo for:

- host setup and configuration
- storage planning and implementation
- hardening and service baselines
- local operational notes, runbooks, and state snapshots
- documentation for how Cirrus fits into the larger lab
- the Cirrus-local comic intake, metadata, and Mylar handoff workflow

Do not use this repo as the source of truth for:

- comics-lab organization-wide governance
- cross-repo architecture policy
- project-specific application requirements outside Cirrus itself

Those belong in a separate lab-architecture or comics-lab repo once the host is stable.

The comic workflow in this repo is host-local implementation detail. It must not be
treated as organization-wide metadata policy. Its authoritative outputs are the
tracked scripts, reports, and the metadata contract in
`docs/comic-metadata-intake-contract.md`.

## Current Priority

Cirrus is still in setup/configuration. Favor present-state accuracy over future-state design.

Work in this order:

1. establish current host truth
2. finish setup and hardening
3. settle storage roles and data placement
4. define service baselines
5. only then expand to broader lab integration

For comic intake work, apply the same order inside the service layer:

1. preserve the original archive and provenance
2. validate the archive and identify its edition type
3. resolve metadata from local sources before remote APIs
4. write and validate `ComicInfo.xml` and `MetronInfo.xml`
5. organize into the Mylar-compatible staging tree
6. promote only when the report says the archive is safe for the target consumer

## Documentation Rules

Keep root docs focused and current.

Preferred root documents:

- `README.md`: what this repo is and how to navigate it
- `CURRENT_STATE.md` or equivalent: what is true now
- `SETUP_PLAN.md` or equivalent: what remains to be done
- `STORAGE.md`: storage roles, mounts, and rules
- `HARDENING.md`: security posture and pending work
- `SERVICES.md`: service inventory and deployment rules
- `CONVERSATION.md`, `BOOKMARKS.md`, `Action-Log.md`: local logs

If existing files overlap, prefer consolidation over duplication.

## Logging Policy

Keep local logs in the repo root:

- `CONVERSATION.md`
- `BOOKMARKS.md`
- `Action-Log.md`

Log significant decisions, setup milestones, and verification steps.

## Operating Guardrails

- Do not treat draft architecture notes as implemented reality.
- Do not introduce services before storage and hardening decisions are documented.
- Do not make destructive storage changes without explicit rollback notes.
- Prefer simple, inspectable host configuration over orchestration or abstraction.
- Treat this repo as the working truth for Cirrus only.

## AI Agent Direction

For now, any agent operating in this repo should behave as a Cirrus host agent:

- understand this machine's capabilities and constraints
- maintain clear boundaries around what Cirrus is allowed to host
- document assumptions and changes
- prepare clean handoff material for later integration into the larger lab

If a future master-agent architecture is defined, this repo should supply host capabilities and constraints to that system rather than define the system itself.

## Comic Intake Agent Boundaries

The comic intake agent is a bounded specialist, not a general host administrator.

- It may inspect and modify staged comic archives under the configured intake roots.
- It must not modify the CBL source files or authoritative cache rows automatically when
  resolving ambiguity; corrections are review artifacts until explicitly approved.
- It must keep source, match, confidence, provenance, and disposition in a machine-readable
  report for every processed archive.
- It must distinguish Mylar-ready from Kavita-readable. A book can be valid for Kavita
  while remaining in review instead of entering Mylar's automated basket.
- It must use local GCD, CBL, sidecar, and existing embedded metadata before ComicVine or
  other rate-limited remote services.
- It must not use concurrency to defeat ComicVine throttles. Parallelism is limited to
  local archive inspection and XML generation; remote requests remain rate-limited and
  cache-backed.
