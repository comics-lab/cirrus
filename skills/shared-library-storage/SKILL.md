---
name: shared-library-storage
description: Design storage layout and access policy for large shared media libraries used by multiple acquisition, organization, and reading services. Use when several applications and a human operator need reliable access to the same long-lived files, with some services writing, others reading, and the library expected to grow substantially over time.
---

# Shared Library Storage

## Overview

Plan storage for a large media library that multiple applications will touch over time. Use this skill when the problem is not just “where do files live,” but “which applications write, which only read, how does the directory layout scale, and how do permissions stay sane as the library grows.”

## Workflow

1. Read the current storage docs, service docs, and latest snapshot.
2. Identify the application roles that will touch the library.
3. Separate acquisition, organization, library-serving, and backup paths.
4. Decide writer versus reader policy before choosing permissions.
5. Document a layout and ownership model that can survive growth and new services.

## Start With

- `CURRENT_STATE.md`
- `logical_storage.md` or equivalent
- `SERVICES.md`
- `SETUP_PLAN.md`
- latest host snapshot file

## Library Questions To Answer First

Decide these before writing compose files or app configs:

1. How much data exists now, and what is the likely growth path?
2. Which applications acquire or rename files?
3. Which applications organize or enrich metadata?
4. Which applications only index or serve files?
5. What should be treated as durable library content versus staging or scratch space?
6. Which paths should be writable by multiple applications, and which should have a single designated writer?

## Layout Principles

For large shared libraries, split paths by role:

- long-lived curated library
- incoming or acquisition area
- organizer working area if needed
- service state or metadata separate from the library itself
- backups separate from live working paths

Do not mix app state, staging, and curated media in one writable tree if you can avoid it.

## Access Model

Prefer:

- one designated writer per library tree where possible
- readers mounted read-only when practical
- separate service-state paths from media-library paths
- shared group plus setgid plus default ACLs only where shared write access is truly needed

If multiple applications must write the same tree, document why and define the collision policy up front.

For very large comic or book libraries, distinguish clearly between:

- intake writers
- organizer writers
- curated-library writers
- reader-only applications
- human administrative access

Do not collapse all of these into one broad shared-write policy unless there is no better operational boundary.

When a human operator also needs remote access from tools like mobile file browsers:

- prefer `SFTP` over the existing SSH service first
- keep the remote protocol aligned with the same user, group, and ACL model used locally
- avoid adding a second file-sharing stack just to browse or manually correct library content

## Scale Rule

When the library is already in the tens of terabytes or expected to grow that large:

- optimize for stable layout and operational clarity first
- avoid designs that require future mass reshuffles
- leave room for additional acquisition, organizer, and reader services
- avoid assuming a two-app model if the roadmap is really five or more actors

## Writeback Rules

Update:

- `logical_storage.md` for the library layout and access policy
- `CURRENT_STATE.md` for implemented storage truth
- `SERVICES.md` when service roles depend on reader versus writer policy
- `SETUP_PLAN.md` if the storage decision unblocks application deployment
- `Action-Log.md` for significant design decisions and verification

## Guardrails

- Do not let every service become a writer to the same library tree by default.
- Do not bury staging or repair work inside the curated library paths.
- Do not put long-lived media policy in a container file before it is documented at the host-storage level.
- Prefer explicit path roles over application-specific improvisation.

## Resources

- `references/multi-app-library-patterns.md`
  Use for reusable guidance on multi-application media libraries, writer versus reader splits, and directory roles for large long-lived collections.
