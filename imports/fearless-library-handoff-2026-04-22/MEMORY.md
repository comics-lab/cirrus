# MEMORY — Fearless Library

## Stable Facts

- Working directory target: `/mnt/fearless/LIBRARY`
- Host context for this tree: `reality.local`
- This tree is meant for direct library work, not host-policy documentation

## Important Related Context

- A prior Codex session repaired and verified the direct `fearless` path well enough for Cirrus-side checks.
- `reality.local:/mnt/fearless` is the good path.
- `reality.local:/export/fearless` is still the bad path and may appear empty or otherwise wrong.

## Existing Local Artifacts

- `MISSING_ISSUES.md`
- `FOUND_FILES/`

## Session Restart Memory

When restarting Codex here, tell it to:
- read `AGENTS.md`
- read `README.md`
- read `HANDOFF.md`
- read `MEMORY.md`
- then inspect `MISSING_ISSUES.md` and the live publisher directories

## Additional Stable Context

- `cirrus` is the host currently used for Mylar-side verification in this workflow.
- Local Mylar project path: `/home/rmleonard/Projects/mylar-library`
- Local Mylar DB path: `/home/rmleonard/Projects/mylar-library/mylar.db`
- Expected Mylar HTTP root from config: `/library/` on port `8690`
- A stale `library.pid` may exist even when Mylar is not running; verify actual service reachability instead of trusting the pidfile.

## Likely Work Areas

- issue-gap tracking
- found-file reconciliation
- library organization checks inside publisher directories
