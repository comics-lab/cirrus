# Cirrus Agent Registry

This is the Cirrus-local routing table. It is adapted from the agent registry pattern in
`../Manage`; it does not make Cirrus subordinate to Manage's Arthur hierarchy.

## Agents

| Agent | Persona/contract | Trigger | Scope | Outputs | Skills |
| --- | --- | --- | --- | --- | --- |
| Cirrus Host Agent | [`AGENTS.md`](../AGENTS.md) | Host setup, storage, services, hardening, local operations | Maintain current host truth and safe local operations | State docs, runbooks, verification | Host truth, storage, hardening, services, resume |
| Comic Metadata Intake Agent | [`skills/comic-metadata-intake/SKILL.md`](../skills/comic-metadata-intake/SKILL.md), [`Agent_Contracts/Comic_Metadata_Intake_Agent.md`](Agent_Contracts/Comic_Metadata_Intake_Agent.md) | CBZ parsing, metadata enrichment, XML creation, intake staging | Resolve and materialize comic metadata with provenance | Validated XML, resolution records, review queues | Comic Metadata Intake |
| Library Ingest Agent | [`Agent_Contracts/Library_Ingest_Agent.md`](Agent_Contracts/Library_Ingest_Agent.md) | Library discovery, source inventory, tagging, layout validation | Maintain reversible library construction workflows | Ingest plans, integrity reports, rollback notes | [`skills/library-ingest/SKILL.md`](../skills/library-ingest/SKILL.md) |
| Mylar Handoff Agent | [`Agent_Contracts/Mylar_Handoff_Agent.md`](Agent_Contracts/Mylar_Handoff_Agent.md) | Promotion, Mylar import verification, post-import checks | Move only approved records into the Mylar basket and verify consumption | Promotion manifest, import results, retry queue | Comic Metadata Intake |

## No Manager/Sub-Agent Hierarchy

Cirrus currently has no managing agent or independent sub-agents. The agents above are
bounded operating roles implemented through documentation and scripts. A future manager may
route work, but must not override the host guardrails or the metadata contract.

## Selection Rule

Use the narrowest applicable role. If a request spans host state and comic ingestion, the
Cirrus Host Agent owns the host boundary and delegates the archive work to the Comic Metadata
Intake or Mylar Handoff role.

## Required Contract Rule

Every future agent role must have:

- a trigger and explicit scope
- input and output definitions
- mutation and approval boundaries
- validation criteria
- rollback or review behavior
- a linked skill when repeatable procedures are involved
