# AGENTS.md - <Cirrus Child Scope>

Use this template for a bounded child scope such as a publisher, library, or service
workflow. It is adapted from `../Manage/templates/AGENTS-child.md` and must remain within
Cirrus's host and local-library boundaries.

## Scope

- **In scope:** <directories, service, or workflow>
- **Out of scope:** <paths and systems this scope must not change>
- **External dependencies:** <databases, APIs, containers, or other repos>

## Role

- **Owner agent:** <agent name>
- **Contract:** <relative contract path>
- **Required skills:** <skill paths>

## Local Truth

- **Current state:** <path>
- **Input manifest/report:** <path>
- **Output manifest/report:** <path>
- **Last verified:** <timestamp>

## Mutation Boundaries

- Read-only actions: <commands or paths>
- Reversible writes: <commands or paths>
- Explicit approval required: <moves, deletes, remote/API actions>
- Never modify: <source data, secrets, canonical caches>

## Handoff

Record the original path, hash, metadata provenance, disposition, validation result, and next
action in a machine-readable report before handing work to another scope.
