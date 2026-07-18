# Agent, Skill, and Contract Inventory

This document describes the definitions currently present in the Cirrus repository. It
records implemented structure only; it does not imply a multi-agent hierarchy where none
exists.

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
the skill for discovery; they do not create an agent or make the skill a sub-agent.

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
