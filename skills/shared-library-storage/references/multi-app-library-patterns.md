# Multi-App Library Patterns

## Distinct Roles

For large comic and book collections, separate these roles conceptually even if some are served by the same app:

- acquisition
- staging or incoming
- organizer or post-processor
- curated library
- reader or serving application
- backup or export

## Preferred Writer Model

Prefer:
- one primary writer for a curated library tree
- one or more acquisition writers for `incoming`
- reader apps using curated libraries read-only where possible
- human admin access using the same shared group model, but not as an excuse to make every application a writer everywhere

This reduces rename collisions, permission drift, and accidental metadata churn.

## Directory Pattern

Typical pattern:

- `media/comics`
- `media/books/ebooks`
- `media/books/other`
- `media/incoming`
- `services/<app>`
- `backups`
- `staging`

Expand under `incoming` or `staging` only when you need separate acquisition pipelines.

## Permission Pattern

Good default:
- shared media group
- setgid directories on shared writable trees
- default ACLs for inherited group access
- no world-writable permissions

Use a more restrictive model for curated library paths when only one app should write there.

## Remote Administrative Access

For manual remote access to a large shared library:

- prefer `SFTP` if the host already has an SSH hardening baseline
- use the same real user and shared group model as local administration
- avoid creating protocol-specific permission islands that diverge from the documented storage policy

Add `SMB3` only when:
- a specific client workflow genuinely needs share semantics
- the exported paths can be kept narrow and deliberate
- the SMB layer will not become the hidden source of truth for permissions

## Scale Considerations

When the collection is very large:
- avoid future path churn
- keep app metadata out of the media tree
- document which service owns renames and file moves
- reserve room for later backup, snapshot, or multi-device expansion
