# Cirrus Agentic System Reference

This document describes the agentic information currently present in the Cirrus repository.
It is the practical reference for adding AI assistance without confusing host operations,
comic-library ingestion, and cross-repository governance. It records implemented structure
only; it does not imply a multi-agent hierarchy where none exists.

## How To Use This Document

1. Read [`AGENTS.md`](../AGENTS.md) for Cirrus scope and guardrails.
2. Use [`Agent_Registry.md`](Agent_Registry.md) to identify the narrowest role.
3. Use [`Director_Routing_Matrix.md`](Director_Routing_Matrix.md) to route the request.
4. Load the selected skill and contract before changing behavior.
5. Run the smallest relevant script, save a report, and validate the result.

The repository is the source of truth for Cirrus-local behavior. `../Manage` remains the
source of truth for organization-wide agent governance and cross-repository management.

## Current Agent Structure

| Agent or control layer | Location | Role | Managing agent | Sub-agents |
| --- | --- | --- | --- | --- |
| Cirrus host agent | [`AGENTS.md`](../AGENTS.md) | Repository-scoped host, storage, service, and local comic-intake guidance | None | None |
| Comic Metadata Intake Agent | [`skills/comic-metadata-intake/SKILL.md`](../skills/comic-metadata-intake/SKILL.md) | Comic archive metadata resolution and staging | [`docs/comic-metadata-intake-contract.md`](comic-metadata-intake-contract.md) | None |
| Library Ingest Agent | [`docs/Agent_Contracts/Library_Ingest_Agent.md`](Agent_Contracts/Library_Ingest_Agent.md) | Reversible library discovery, enrichment, and layout work | [`skills/library-ingest/SKILL.md`](../skills/library-ingest/SKILL.md) | None |
| Mylar Handoff Agent | [`docs/Agent_Contracts/Mylar_Handoff_Agent.md`](Agent_Contracts/Mylar_Handoff_Agent.md) | Approved promotion and post-import verification | [`skills/comic-metadata-intake/SKILL.md`](../skills/comic-metadata-intake/SKILL.md) | None |
| Imported library handoff agent guidance | [`imports/fearless-library-handoff-2026-04-22/AGENTS.md`](../imports/fearless-library-handoff-2026-04-22/AGENTS.md) | Historical handoff material for the imported library | None; inactive in the Cirrus root | None |
| Imported FOUND_FILES guidance | [`imports/fearless-library-handoff-2026-04-22/FOUND_FILES/AGENTS.md`](../imports/fearless-library-handoff-2026-04-22/FOUND_FILES/AGENTS.md) | Historical found-file handoff instructions | None; inactive in the Cirrus root | None |
| Reality library handoff template | [`templates/reality-library-handoff/AGENTS.md`](../templates/reality-library-handoff/AGENTS.md) | Template for another host/library handoff | None; template only | None |

There is currently no `agents-master.md`, `agents.md`, manager agent, orchestration
contract, or registered sub-agent definition in this repository.

The root `AGENTS.md` is the active operating profile. The imported `AGENTS.md` files and
the handoff template are reference artifacts, not active child agents.

## Skills And Contracts

| Skill | Location | Primary purpose | Contract used | References/resources |
| --- | --- | --- | --- | --- |
| Comic Metadata Intake | [`skills/comic-metadata-intake/SKILL.md`](../skills/comic-metadata-intake/SKILL.md) | Inspect, resolve, validate, materialize, and stage comic archives for Mylar/Kavita | [`docs/comic-metadata-intake-contract.md`](comic-metadata-intake-contract.md) | Existing intake utilities and reports |
| Host Truth Capture | [`skills/host-truth-capture/SKILL.md`](../skills/host-truth-capture/SKILL.md) | Capture live host state and update current-state documentation | None | [`linux-host-snapshot.md`](../skills/host-truth-capture/references/linux-host-snapshot.md) |
| Host Storage Baseline | [`skills/host-storage-baseline/SKILL.md`](../skills/host-storage-baseline/SKILL.md) | Define storage roles, mounts, subvolumes, ownership, and placement | None | [`storage-patterns.md`](../skills/host-storage-baseline/references/storage-patterns.md) |
| Shared Library Storage | [`skills/shared-library-storage/SKILL.md`](../skills/shared-library-storage/SKILL.md) | Define multi-application library layout and writer/reader policy | None | [`multi-app-library-patterns.md`](../skills/shared-library-storage/references/multi-app-library-patterns.md) |
| Host Hardening Baseline | [`skills/host-hardening-baseline/SKILL.md`](../skills/host-hardening-baseline/SKILL.md) | Review SSH, firewall, logging, SMART, power, and service exposure | None | [`hardening-checks.md`](../skills/host-hardening-baseline/references/hardening-checks.md) |
| Service Baseline Review | [`skills/service-baseline-review/SKILL.md`](../skills/service-baseline-review/SKILL.md) | Classify enabled services against the Cirrus host role | None | [`service-classification.md`](../skills/service-baseline-review/references/service-classification.md) |
| Host Resume Handoff | [`skills/host-resume-handoff/SKILL.md`](../skills/host-resume-handoff/SKILL.md) | Create restart checkpoints and next-session instructions | None | [`resume-checklist.md`](../skills/host-resume-handoff/references/resume-checklist.md) |

Each skill also has UI metadata in its local `agents/openai.yaml` file. Those files describe
the skill for discovery; they do not create an agent or make the skill a sub-agent. The
general `library-ingest` skill currently has no `agents/openai.yaml` metadata file.

## Skill Details And Behaviors

| Skill | Behavior/persona | Important references | Typical outputs |
| --- | --- | --- | --- |
| `comic-metadata-intake` | Bounded comic specialist; local-first resolution, provenance, confidence, rate-limited remote lookup, separate Kavita/Mylar readiness | [`comic-metadata-intake-contract.md`](comic-metadata-intake-contract.md) | XML, resolution report, review queue, staged archive |
| `library-ingest` | Reversible source discovery, enrichment, tagging, duplicate analysis, and layout construction | [`Library_Ingest_Agent.md`](Agent_Contracts/Library_Ingest_Agent.md) | Inventory, ingest plan, integrity report, rollback notes |
| `host-truth-capture` | Establish live host truth before making storage, service, or deployment decisions | [`linux-host-snapshot.md`](../skills/host-truth-capture/references/linux-host-snapshot.md) | Current-state update, snapshot, action log |
| `host-storage-baseline` | Define disks, filesystems, mounts, Btrfs subvolumes, ownership, and service-data placement | [`storage-patterns.md`](../skills/host-storage-baseline/references/storage-patterns.md) | Storage plan, mount verification, placement rules |
| `shared-library-storage` | Separate durable library, intake, organizer, service state, and backup roles; define writers/readers | [`multi-app-library-patterns.md`](../skills/shared-library-storage/references/multi-app-library-patterns.md) | Library layout and access policy |
| `host-hardening-baseline` | Review remote access, firewall, logging, SMART, power, and exposed services | [`hardening-checks.md`](../skills/host-hardening-baseline/references/hardening-checks.md) | Hardening checklist and remaining-risk record |
| `service-baseline-review` | Classify services as required, intentional convenience, unclear, or removal candidate | [`service-classification.md`](../skills/service-baseline-review/references/service-classification.md) | Service baseline and review queue |
| `host-resume-handoff` | Create precise restart checkpoints after changes, incidents, or pauses | [`resume-checklist.md`](../skills/host-resume-handoff/references/resume-checklist.md) | `RESUME.md`, action-log entry, next checks |

## Contracts And Responsibilities

Contracts define responsibilities and acceptance criteria; skills define repeatable operating
behavior. The two should remain linked but not duplicated.

| Contract | Responsible role | Core behavior | Acceptance boundary |
| --- | --- | --- | --- |
| [`comic-metadata-intake-contract.md`](comic-metadata-intake-contract.md) | Comic Metadata Intake Agent | Inspect, resolve, materialize, and classify archives | Valid XML, provenance, confidence, and explicit disposition |
| [`Agent_Contracts/Comic_Metadata_Intake_Agent.md`](Agent_Contracts/Comic_Metadata_Intake_Agent.md) | Comic Metadata Intake Agent | Field-level identity resolution and mutation boundaries | No silent source correction; review conflicts |
| [`Agent_Contracts/Library_Ingest_Agent.md`](Agent_Contracts/Library_Ingest_Agent.md) | Library Ingest Agent | Reversible discovery and stable library construction | Integrity report and rollback path |
| [`Agent_Contracts/Mylar_Handoff_Agent.md`](Agent_Contracts/Mylar_Handoff_Agent.md) | Mylar Handoff Agent | Promote approved records and verify Mylar/Kavita outcomes | Only `mylar_ready` records are promoted |

No formal contracts yet exist for host truth, storage, hardening, service baseline, or resume
handoff. Their current behavior is defined by the corresponding skills and root documents.

## Contract Inventory

| Contract | Location | Consumers | Scope |
| --- | --- | --- | --- |
| Comic Metadata Intake Contract | [`docs/comic-metadata-intake-contract.md`](comic-metadata-intake-contract.md) | Comic Metadata Intake skill; intake/resolver/materializer/promotion utilities | Archive states, provenance, source precedence, XML requirements, confidence, and Mylar handoff |
| Library Ingest Agent Contract | [`docs/Agent_Contracts/Library_Ingest_Agent.md`](Agent_Contracts/Library_Ingest_Agent.md) | Library Ingest Agent | Reversible discovery, enrichment, layout, and integrity validation |
| Comic Metadata Intake Agent Contract | [`docs/Agent_Contracts/Comic_Metadata_Intake_Agent.md`](Agent_Contracts/Comic_Metadata_Intake_Agent.md) | Comic Metadata Intake Agent | Identity resolution, provenance, mutation boundaries, and XML validation |
| Mylar Handoff Agent Contract | [`docs/Agent_Contracts/Mylar_Handoff_Agent.md`](Agent_Contracts/Mylar_Handoff_Agent.md) | Mylar Handoff Agent | Approved promotion and post-import verification |

No formal contracts currently exist for host truth, storage, hardening, services, or resume
handoffs. Those areas are governed by their skill instructions and root documentation.

## Practical Relationship

```text
Cirrus host agent guidance
  +-- host truth / storage / hardening / services / resume skills
  +-- shared library storage skill
  +-- comic metadata intake skill
        +-- comic metadata intake contract
              +-- inspect -> resolve -> materialize -> promote
```

The comic workflow is not currently delegated to multiple agents. The preferred design is a
single bounded intake specialist using deterministic scripts and saved reports. Parallelism
should be reserved for local archive inspection and XML generation; ComicVine requests remain
single-threaded, cached, and rate-limited.

## Executable Assistance Surface

AI assistance should orchestrate existing deterministic tools rather than reimplement their
logic conversationally.

| Stage | Primary implementation | Input | Output or gate |
| --- | --- | --- | --- |
| Cache refresh | `utilities/build_cbl_cache.py` | CBL reading lists | SQLite ComicVine lookup cache |
| Prepass | `utilities/prepass_normalize.py` | CBZ, sidecars, local cache | Normalized metadata and report |
| Archive audit | `utilities/cbz_audit.py` | CBZ tree | Validity and Mylar-readiness report |
| Cleanup | `scripts/file_cleanup_parallel.sh` and `scripts/file_cleanup_apply.sh` | CBZ tree or saved JSON plan | Duplicate/error/review lanes |
| Metadata resolution | `utilities/resolve_issue_from_local_metadata.py` and `utilities/cv_issue_resolver.py` | Local metadata and optional APIs | Candidate IDs and confidence report |
| XML writing | `utilities/pass1_write_comicinfo.py` | Approved ComicVine/local match | Root ComicInfo and post-write audit |
| v3 organization | `utilities/mylar_v3_buildout.py` | Staged CBZ branches | Mylar-shaped tree, sidecars, provenance |
| Promotion | `utilities/promote_mylar_import.py` | Mylar-valid archives | Mylar import basket and report |
| Full orchestration | `utilities/intake_pipeline.py` and `scripts/refresh_intake_pipeline.sh` | Post-conversion CBZ root | End-to-end report set |
| Mylar verification | Existing Mylar API/log procedures | Import basket and service state | Recheck, metatag, and import result |

The intended future interface is a saved JSON resolution/materialization plan between
resolution and mutation. That plan makes retries idempotent, reduces repeated archive reads,
and gives another agent or machine a safe handoff artifact.

## AI Assistance Rules

- Use the host role for mounts, Docker, permissions, service state, and system changes.
- Use the comic role for CBZ identity, XML, CBL/GCD/Metron/ComicVine, and intake staging.
- Use the library role for inventory, duplicate analysis, and broad layout changes.
- Use the Mylar handoff role only after metadata and archive gates pass.
- Keep remote ComicVine requests sequential and cached; local work may be parallelized.
- Require dry-run reports before bulk renames, moves, overwrites, or cleanup.
- Preserve original filename, path, hash, source, confidence, and disposition.
- Never silently change CBL source files or canonical cache rows.
- Treat `kavita_ready` and `mylar_ready` as different states.
- Do not claim Mylar acceptance until logs/API/database state confirm it.

## Missing Or Future Components

These are useful future additions, not currently implemented agents:

- `intake-inspector`: read-only archive and sidecar inspection
- `metadata-resolver`: local database matching and rate-limited remote lookup
- `metadata-materializer`: approved JSON plan to XML/path materialization
- `mylar-handoff`: promotion and post-import verification
- `monitor-action`: queue depth, service health, and API failure monitoring
- a Cirrus-specific master profile, if a real manager role becomes necessary

Before adding any of these, define its input/output schema, owned paths, approval boundary,
retry behavior, idempotency rule, and contract tests. Prefer subprocess/workflow roles before
creating independent conversational agents.

## Wiki And Navigation

This document is included automatically by the docs-mode wiki sync because it is under
`docs/`. The sync script publishes it as `docs-agent-skill-contract-inventory.md` and adds it
to `_Sidebar.md`. The repository README links it in both the Start Here list and the Index.

## Recommended Future Additions

If the project later needs multiple agents, add them only with explicit boundaries:

- `intake-inspector`: read-only archive and sidecar inspection
- `metadata-resolver`: local database matching and rate-limited remote lookup
- `metadata-materializer`: apply an approved JSON plan and validate XML
- `mylar-handoff`: promote only records marked `mylar_ready`, then verify import

These should be subprocess or workflow roles before becoming independent conversational agents.
Each would need an input/output schema, ownership of directories, retry behavior, and a
conflict policy. Until those are implemented, the existing Python pipeline remains the
authoritative execution path.
