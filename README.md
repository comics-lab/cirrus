# Cirrus

This repo is the working notebook and operational documentation for the `cirrus` machine.

Cirrus is currently in setup and configuration. Until that work is complete, this repo should describe present host reality first and future lab architecture second.

## Purpose

Use this repo to track:

- host state and hardware snapshots
- storage layout and mount decisions
- security hardening status
- service deployment prerequisites and baselines
- local runbooks, notes, and setup history

This repo is not the source of truth for comics-lab organization policy. It may later feed a broader lab-architecture project after Cirrus is stable.

## Start Here

- `CURRENT_STATE.md`: concise implemented truth for the host
- `docs/token-efficiency.md`: guidance on reducing token use with files, scripts, and bounded work
- `docs/wiki-sync.md`: GitHub wiki sync setup and required secret
- `docs/media-server-maintenance.md`: update/install guide for Mylar, Kavita, and Komga
- `docs/intake-to-mylar-workflow.md`: step-by-step JDownloader to Mylar import workflow
- `docs/intake-flow-diagram.md`: one-page visual map of the intake and handoff path
- `docs/cbl-readinglists-cache.md`: local ComicVine cache from CBL reading lists
- `docs/cbl-cache-collection-analysis.md`: collector-style analysis of the CBL cache
- `docs/comicvine-ambiguity-verification.md`: review-only ComicVine ambiguity verifier
- `docs/local-metadata-to-comicvine-resolution.md`: local GCD/Metron to ComicVine resolution flow
- `docs/prepass-normalization.md`: normalization stage before Pass 1
- `docs/mylar-v3-buildout.md`: v3-only buildout normalizer for Mylar-shaped trees
- `docs/comic-metadata-intake-contract.md`: metadata, provenance, confidence, and handoff contract
- `docs/agent-skill-contract-inventory.md`: current agents, skills, contracts, and ownership map
- `docs/Agent_Registry.md`: Cirrus-local agent roles and responsibilities
- `docs/Director_Routing_Matrix.md`: deterministic request routing
- `skills/comic-metadata-intake/SKILL.md`: bounded comic parser/intake agent guidance
- `scripts/pass1_batch.sh`: shell wrapper for Pass 1
- `scripts/promote_mylar_import.sh`: shell wrapper for promotion into Mylar staging
- `scripts/pass1_then_promote.sh`: combined Pass 1 plus promotion wrapper
- `scripts/mylar_v3_buildout.sh`: v3-only Mylar buildout wrapper
- `scripts/file_cleanup.sh`: report-first intake cleanup, quarantine, and provenance-preserving wrapper
- `scripts/file_cleanup_parallel.sh`: preconfigured parallel cleanup wrapper
- `scripts/file_cleanup_apply.sh`: apply a previously generated cleanup report without rescanning
- `scripts/refresh_intake_pipeline.sh`: full refresh pipeline from cache rebuild through pass1/promote
- `utilities/intake_pipeline.py`: single Python entrypoint for the post-conversion intake pipeline
- `docs/btrfs-swapfile.md`: dedicated Btrfs subvolume swapfile setup
- `SETUP_PLAN.md`: ordered next work for Cirrus
- `SERVICES.md`: current live service baseline and keep/drop review queue
- `RESUME.md`: normalized session handoff for the next restart
- `NEXT_STEPS_2026-03-15.md`: restructuring assessment and rationale
- `state-of-hardware-20260315-230117.txt`: post-change host snapshot
- `state-of-hardware-20260315-220018.txt`: current live host snapshot
- `state-of-hardware-20260126-055629.txt`: baseline host snapshot
- `cirrus_checklist.md`: older staged bring-up checklist
- `hardening.md`: detailed hardening notes
- `logical_storage.md`: storage roles and rules

## Index

Current root docs:

- `AGENTS.md`: repo-scoped operating guidance for agents
- `README.md`: repo purpose and navigation
- `CURRENT_STATE.md`: implemented host truth
- `docs/token-efficiency.md`: token-saving operating model and repo workflow guidance
- `docs/wiki-sync.md`: wiki sync setup and secret/bootstrap notes
- `docs/media-server-maintenance.md`: Docker maintenance guide for Mylar, Kavita, and Komga
- `docs/intake-to-mylar-workflow.md`: operational flow from raw intake to Mylar import
- `docs/intake-flow-diagram.md`: one-page visual map of the intake and handoff path
- `docs/cbl-readinglists-cache.md`: cached ComicVine lookup support from `.cbl` files
- `docs/cbl-cache-collection-analysis.md`: collector-oriented analysis of cache uniqueness and ambiguity
- `docs/comicvine-ambiguity-verification.md`: review-only ComicVine metadata verification flow
- `docs/local-metadata-to-comicvine-resolution.md`: resolver for turning local metadata into ComicVine issue ids
- `docs/prepass-normalization.md`: pre-Pass 1 normalization stage
- `docs/mylar-v3-buildout.md`: staged buildout normalization for Mylar naming
- `docs/comic-metadata-intake-contract.md`: contract for parser output and consumer handoff
- `docs/agent-skill-contract-inventory.md`: agent, skill, and contract inventory
- `docs/Agent_Registry.md`: local agent registry
- `docs/Director_Routing_Matrix.md`: local routing matrix
- `scripts/pass1_batch.sh`: Pass 1 shell wrapper
- `scripts/promote_mylar_import.sh`: promotion shell wrapper
- `scripts/pass1_then_promote.sh`: combined handoff shell wrapper
- `scripts/mylar_v3_buildout.sh`: v3 buildout shell wrapper
- `scripts/verify_comicvine_ambiguity.sh`: ComicVine ambiguity verifier wrapper
- `scripts/resolve_issue_from_local_metadata.sh`: local metadata to ComicVine resolver wrapper
- `scripts/file_cleanup.sh`: file and directory cleanup wrapper with JSON reports and quarantine staging
- `scripts/file_cleanup_parallel.sh`: parallel cleanup wrapper with a preset worker count
- `scripts/file_cleanup_apply.sh`: replay a saved cleanup report as an apply step
- `scripts/refresh_intake_pipeline.sh`: end-to-end intake refresh wrapper
- `utilities/intake_pipeline.py`: consolidated Python pipeline entrypoint
- `skills/comic-metadata-intake/SKILL.md`: comic metadata intake skill
- `skills/library-ingest/SKILL.md`: general reversible library-ingest skill
- `docs/btrfs-swapfile.md`: Btrfs swapfile setup using a dedicated subvolume
- `SETUP_PLAN.md`: ordered remaining work
- `SERVICES.md`: service inventory and baseline decision point
- `RESUME.md`: next-session restart point
- `NEXT_STEPS_2026-03-15.md`: March restructuring rationale

Reference and working notes:

- `state-of-hardware-20260315-230117.txt`: latest post-change host snapshot
- `state-of-hardware-20260315-220018.txt`: latest captured live host snapshot
- `state-of-hardware-20260126-055629.txt`: captured host snapshot
- `cirrus_checklist.md`: older bring-up checklist with captured state
- `hardening.md`: hardening checklist plus observed status
- `logical_storage.md`: storage roles plus current implementation notes
- `restart.md`: January restart checkpoint
- `REPLY_beast-storage-plan_20260125-2147.txt`: saved external planning note

## Logs

- `CONVERSATION.md`
- `BOOKMARKS.md`
- `Action-Log.md`

## Documentation Notes

The root documentation still contains some older working notes, but the intended structure is now:

- keep host truth and setup tasks at the root
- keep larger lab book material under `the_lab/`
- move org-wide architecture work into a separate project after Cirrus setup is complete

## Wiki Sync

This repo now includes a GitHub Actions workflow to sync selected markdown docs into the repository wiki.

Required secret:

- `WIKI_PUSH_TOKEN`: a token with permission to push to the repository wiki

The workflow syncs:

- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `RESUME.md`
- `Action-Log.md`
- `docs/**`
