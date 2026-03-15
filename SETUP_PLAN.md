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

## Phase 2: Host Identity Decision

Decide explicitly whether Cirrus is:

- a server with GNOME temporarily present
- or a workstation that also runs services

That decision affects:

- which services should stay enabled
- whether dual network paths are acceptable
- how aggressive hardening should be
- whether local desktop convenience can override service-host discipline
- the keep/drop decisions listed in `SERVICES.md`

## Phase 3: Hardening Completion

- review enabled services and disable what is not required
- review wired and Wi-Fi policy
- confirm sudo, SSH, firewall, and logging posture
- decide whether `fail2ban` and `auditd` are needed
- capture a fresh post-cleanup state snapshot
- use `state-of-hardware-20260315-220018.txt` as the pre-change baseline

## Phase 4: Phoenix Decision

Resolve Phoenix before Docker or app deployment.

Questions to answer:

- Is Phoenix intended to hold durable service data? Current answer: yes.
- What top-level directories or Btrfs subvolumes should exist on Phoenix?
- What directory layout should exist on Phoenix?
- What ownership and permissions model will be used?

Current state:

- Phoenix has already been wiped and recreated as a clean Btrfs volume
- selected initial layout: the lean Phoenix subvolume set documented in `logical_storage.md`
- the lean Phoenix subvolume layout has been created
- ownership and service-write policy are now documented in `logical_storage.md`
- shared group and ACL baseline have been applied on the live host

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
