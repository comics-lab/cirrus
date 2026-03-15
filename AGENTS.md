# AGENTS.md — Cirrus

This repo documents and manages the `cirrus` host.

## Scope

This is a machine- and operations-scoped repo, not an org-wide policy repo.

Use this repo for:

- host setup and configuration
- storage planning and implementation
- hardening and service baselines
- local operational notes, runbooks, and state snapshots
- documentation for how Cirrus fits into the larger lab

Do not use this repo as the source of truth for:

- comics-lab organization-wide governance
- cross-repo architecture policy
- project-specific application requirements outside Cirrus itself

Those belong in a separate lab-architecture or comics-lab repo once the host is stable.

## Current Priority

Cirrus is still in setup/configuration. Favor present-state accuracy over future-state design.

Work in this order:

1. establish current host truth
2. finish setup and hardening
3. settle storage roles and data placement
4. define service baselines
5. only then expand to broader lab integration

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
