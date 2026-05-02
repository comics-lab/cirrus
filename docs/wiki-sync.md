# Wiki Sync Setup

Cirrus includes a GitHub Actions workflow that syncs selected markdown docs into the repository wiki.

## What It Syncs

The workflow publishes:

- `README.md`
- `CURRENT_STATE.md`
- `SETUP_PLAN.md`
- `SERVICES.md`
- `RESUME.md`
- `Action-Log.md`
- `docs/**`

## Required Secret

Create a repository secret named:

- `WIKI_PUSH_TOKEN`

Store a GitHub token in that secret with permission to push to the repository wiki.

Recommended token types:

- classic PAT with `repo` scope
- fine-grained PAT with wiki write access if your GitHub setup supports it

## Wiki Bootstrap

If the repository wiki has never been initialized, GitHub may require one manual step first:

1. Open the repository wiki page in GitHub.
2. Create the first page manually.
3. Save it.

After that, the workflow can clone and push to the wiki remote.

## Workflow Behavior

The workflow reads the token from:

- `secrets.WIKI_PUSH_TOKEN`
- or `secrets.wiki_push_token` as a fallback

If neither secret exists, the sync step will fail with a clear error message.

## Local Debug

The sync script can also be run locally in dry-run mode:

```bash
WIKI_DRY_RUN=1 GITHUB_REPOSITORY=owner/repo bash .github/scripts/sync-to-wiki.sh
```

That writes wiki output to a temporary directory without pushing.
