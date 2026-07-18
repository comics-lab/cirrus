# Mylar Handoff Agent Contract

## Purpose

Safely stage approved comic archives for Mylar, verify consumption, and leave Kavita with a
stable organized library.

## Inputs

- Approved resolution/materialization report
- Validated CBZ archives
- Current Mylar `folder_format`, `file_format`, import root, and destination settings
- Existing import and library manifests

## Outputs

- Promotion manifest with source and destination paths
- Collision, rejection, and retry reports
- Mylar API/log verification result
- Post-import library verification for metadata and path

## Guardrails

- Never promote a record marked only `kavita_ready` or `metadata_review`.
- Use dry-run and collision checks before copying or moving.
- Keep one authoritative promotion record per archive hash.
- Do not repeatedly resubmit an archive without checking Mylar logs and database state.
- Do not assume Mylar acceptance means Kavita metadata success; verify both separately.

## Validation

- [ ] Source archive is readable and hash recorded.
- [ ] Root XML is valid and metadata meets Mylar's configured import requirements.
- [ ] Destination path matches the current Mylar configuration.
- [ ] Mylar accepted or explicitly rejected the archive.
- [ ] Recheck/metatag result and final library path are recorded.
