# Next Steps Assessment — 2026-03-15

## Summary

The current `AGENTS.md` is not appropriate for this repo in its present state. It is an org-level `comics-lab` master policy copied verbatim into a machine/setup repo. The rest of the root docs read like a host bring-up notebook for Cirrus, not a comics-lab governance repo.

## Key Mismatches

- `AGENTS.md` describes org-wide repo taxonomy and master-agent behavior, but this repo is currently a single host's build/state record.
- There is no root `README.md`, even though the copied policy requires one.
- The setup docs mix current truth and future architecture. `RESUME.md`, `cirrus_checklist.md`, `hardening.md`, and `architecture.md` overlap heavily.
- Host state is only partially settled: Phoenix is mounted and heavily used, Docker is not installed, and the enabled-service list still looks desktop-heavy.
- The repo already contains a better long-term docs shape under `the_lab/comics-lab-book/`, but most of it is still stubbed.

## Recommended Direction

1. Move `cirrus` out of `~/Projects/comics-lab/` to `~/Projects/cirrus/`.
2. Treat `cirrus` as a machine/ops repo first, not a comics-lab org repo.
3. Replace the current `AGENTS.md` with a local Cirrus-specific agent policy:
   - scope: this host only
   - purpose: setup, hardening, storage, services, documentation
   - boundaries: no org architecture authority, no project-level governance
4. Add a root `README.md` that explains exactly what this repo is and links to `CONVERSATION.md`, `BOOKMARKS.md`, and `Action-Log.md`.
5. Collapse the root docs into a smaller set:
   - `README.md`
   - `CURRENT_STATE.md`
   - `SETUP_PLAN.md`
   - `STORAGE.md`
   - `HARDENING.md`
   - `SERVICES.md`
   - keep logs as-is
6. Finish Cirrus setup before reopening comics-lab architecture work.

## Practical Order

1. Finalize repo identity and docs.
2. Finish host hardening.
3. Resolve Phoenix.
4. Install and configure Docker only after storage is settled.
5. Stand up core services after the above.

## AI Architecture Direction

The proposed structure is sound if it is split into explicit contract layers:

- Master agent: governance, placement policy, conflict resolution, boundary enforcement
- Hardware agents: per-host capability and policy manifests
- Project agents: per-project goals, dependencies, data locality, runtime constraints

The master agent should orchestrate placement and policy, not own project logic.
