#!/usr/bin/env bash

set -euo pipefail

SESSION_ID="019cf372-6836-73d1-aa30-135255a40358"
REPO_DIR="/home/rmleonard/Projects/cirrus"

cd "$REPO_DIR"

if codex resume "$SESSION_ID"; then
  exit 0
fi

cat <<'EOF'
Stored Codex session resume failed.
Starting a fresh Codex session in /home/rmleonard/Projects/cirrus.

If the new session needs context, ask it to read:
- RESUME.md
- Action-Log.md
- SERVICES.md
- logical_storage.md
EOF

exec codex
