# Setup Plan — Cirrus

## Goal

Finish Cirrus as a clean, well-documented host before resuming broader comics-lab architecture work.

## Phase 1: Repo and Documentation Cleanup

- Repo now lives at `/home/rmleonard/Projects/cirrus`
- Keep this repo host-scoped
- Continue reducing root-doc overlap
- Treat `CURRENT_STATE.md` as implemented truth
- Treat this file as forward plan
- Keep restart and bookmark docs aligned with the current repo path and document set
- Review the `docs-normalization` branch diff before merging the documentation cleanup into `main`

## Phase 2: Host Identity Decision

Decide explicitly whether Cirrus is:

- a server with GNOME temporarily present
- or a workstation that also runs services

That decision affects:

- which services should stay enabled
- whether dual network paths are acceptable
- how aggressive hardening should be
- whether local desktop convenience can override service-host discipline

## Phase 3: Hardening Completion

- review enabled services and disable what is not required
- review wired and Wi-Fi policy
- confirm sudo, SSH, firewall, and logging posture
- decide whether `fail2ban` and `auditd` are needed
- capture a fresh post-cleanup state snapshot

## Phase 4: Phoenix Decision

Resolve Phoenix before Docker or app deployment.

Questions to answer:

- Is Phoenix staging-only, or is it intended to hold durable service data?
- Should Phoenix be wiped and rebuilt now?
- What directory layout should exist on Phoenix?
- What ownership and permissions model will be used?

Until that is answered, avoid placing long-lived application data there.

## Phase 5: Container Baseline

Only after hardening and Phoenix are settled:

- install Docker
- define daemon defaults
- decide Docker `data-root`
- establish compose as the canonical deployment method
- create service directory and runbook structure

## Phase 6: Service Bring-Up

Recommended order:

1. reverse proxy, if needed
2. Kavita
3. Mylar
4. any supporting data services only if required
5. monitoring

## Phase 7: Broader Lab Integration

After Cirrus is stable:

- create a separate lab-architecture or next-steps project
- define master-agent, hardware-agent, and project-agent contracts
- integrate Cirrus into the broader comics-lab architecture from a position of host clarity rather than speculation
