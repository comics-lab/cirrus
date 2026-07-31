#!/usr/bin/env bash
set -euo pipefail

# Sync repository markdown content into the GitHub wiki.
#
# Modes:
# - docs: publish docs/**/*.md plus a small set of root operational docs
# - repo: publish all markdown in the repo except excluded paths
# - selected: publish markdown under WIKI_INCLUDE_PATHS
# - empty: publish only Home.md
#
# Environment variables:
# - GITHUB_REPOSITORY (owner/repo)
# - WIKI_PUSH_TOKEN or GITHUB_TOKEN
# - WIKI_SYNC_MODE (docs|repo|selected|empty)
# - WIKI_INCLUDE_PATHS (newline-delimited relative paths for selected mode)
# - WIKI_HOME_SOURCE (relative path for Home.md; defaults to README.md when present)
# - WIKI_DRY_RUN=1 to skip remote wiki access and push for local verification

REPO="${GITHUB_REPOSITORY:-}"
TOKEN="${WIKI_PUSH_TOKEN:-${GITHUB_TOKEN:-}}"
MODE="${WIKI_SYNC_MODE:-docs}"
HOME_SOURCE="${WIKI_HOME_SOURCE:-}"
DRY_RUN="${WIKI_DRY_RUN:-0}"

if [[ -z "$REPO" ]]; then
  echo "GITHUB_REPOSITORY must be set"
  exit 1
fi

if [[ -z "$HOME_SOURCE" && -f README.md ]]; then
  HOME_SOURCE="README.md"
fi

TMP_DIR=$(mktemp -d)
WIKI_DIR="$TMP_DIR/wiki"
MANIFEST="$TMP_DIR/wiki-manifest.tsv"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

slug_for_rel() {
  local rel="$1"
  rel="${rel%.md}"
  rel="${rel//\//-}"
  rel="${rel// /-}"
  printf '%s\n' "$rel"
}

sidebar_title_for() {
  local rel="$1"
  case "$rel" in
    README.md) printf '%s\n' "Home" ;;
    CURRENT_STATE.md) printf '%s\n' "Current State" ;;
    SETUP_PLAN.md) printf '%s\n' "Setup Plan" ;;
    SERVICES.md) printf '%s\n' "Services" ;;
    RESUME.md) printf '%s\n' "Resume" ;;
    Action-Log.md) printf '%s\n' "Action Log" ;;
    docs/token-efficiency.md) printf '%s\n' "Token Efficiency" ;;
    docs/agent-skill-contract-inventory.md) printf '%s\n' "Agentic System Reference" ;;
    *)
      rel="${rel%.md}"
      rel="${rel##*/}"
      rel="${rel//_/ }"
      printf '%s\n' "$rel"
      ;;
  esac
}

mkdir -p "$WIKI_DIR"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run: skipping wiki remote checks and push"
  git -C "$WIKI_DIR" init >/dev/null
else
  if [[ -z "$TOKEN" ]]; then
    echo "WIKI_PUSH_TOKEN or GITHUB_TOKEN must be set unless WIKI_DRY_RUN=1"
    exit 1
  fi

  WIKI_REMOTE="https://x-access-token:${TOKEN}@github.com/${REPO}.wiki.git"
  PUBLIC_WIKI_URL="https://github.com/${REPO}/wiki"

  echo "Checking wiki remote for ${REPO}"
  if ! git ls-remote "$WIKI_REMOTE" >/dev/null 2>&1; then
    cat <<MSG
Wiki remote is not reachable.

Common causes:
- The repository wiki has not been initialized yet.
- The token does not have permission to access the wiki repo.

Fix:
1. Open ${PUBLIC_WIKI_URL}
2. Create the first wiki page manually
3. Add a repository or organization secret named WIKI_PUSH_TOKEN with repo write access
4. Re-run the "Sync docs to Wiki" workflow
MSG
    exit 1
  fi

  echo "Cloning wiki repo for ${REPO}"
  if git clone --depth 1 "$WIKI_REMOTE" "$WIKI_DIR" >/dev/null 2>&1; then
    echo "Cloned existing wiki repo"
  else
    echo "Wiki repo does not exist yet or is empty; initializing a new local wiki worktree"
    rm -rf "$WIKI_DIR"
    mkdir -p "$WIKI_DIR"
    git -C "$WIKI_DIR" init >/dev/null
    git -C "$WIKI_DIR" remote add origin "$WIKI_REMOTE"
  fi
fi

echo "Cleaning wiki working tree"
find "$WIKI_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
: > "$MANIFEST"

append_manifest() {
  local rel="$1"
  [[ -f "$rel" ]] || return 0
  [[ "$rel" == *.md ]] || return 0
  [[ "$rel" == README.md ]] && return 0
  local slug
  slug="$(slug_for_rel "$rel")"
  printf '%s\t%s\n' "$rel" "$slug" >> "$MANIFEST"
}

should_exclude_repo_path() {
  local rel="$1"
  case "$rel" in
    .git/*|.github/*|node_modules/*|vendor/*|dist/*|build/*|coverage/*|logs/*)
      return 0
      ;;
    docs/agents/chats/*|templates/CodingProject_root/starter_pack/*|legacy/*|Documents_archive/*)
      return 0
      ;;
    Scripts/ckeditor/*|Scripts/ckeditor.backup-working-2023-01-27/*|Scripts/ckeditor.tmp/*|Scripts/ckeditor.not-correct-no-autogrow/*)
      return 0
      ;;
  esac
  return 1
}

collect_docs_mode() {
  [[ -d docs ]] || return 0
  while IFS= read -r -d '' src; do
    append_manifest "${src#./}"
  done < <(find ./docs -type f -name '*.md' -print0 | sort -z)

  for rel in README.md CURRENT_STATE.md SETUP_PLAN.md SERVICES.md RESUME.md Action-Log.md; do
    [[ -f "$rel" ]] && append_manifest "$rel"
  done
}

collect_repo_mode() {
  while IFS= read -r -d '' src; do
    local rel="${src#./}"
    if should_exclude_repo_path "$rel"; then
      continue
    fi
    append_manifest "$rel"
  done < <(find . -type f -name '*.md' -print0 | sort -z)
}

collect_selected_mode() {
  if [[ -z "${WIKI_INCLUDE_PATHS:-}" ]]; then
    echo "WIKI_INCLUDE_PATHS must be set for selected mode"
    exit 1
  fi

  while IFS= read -r include; do
    [[ -n "$include" ]] || continue
    if [[ -f "$include" ]]; then
      append_manifest "$include"
      continue
    fi
    if [[ -d "$include" ]]; then
      while IFS= read -r -d '' src; do
        append_manifest "${src#./}"
      done < <(find "./$include" -type f -name '*.md' -print0 | sort -z)
    fi
  done <<< "$WIKI_INCLUDE_PATHS"
}

echo "Building wiki page manifest (mode: $MODE)"
case "$MODE" in
  docs)
    collect_docs_mode
    ;;
  repo)
    collect_repo_mode
    ;;
  selected)
    collect_selected_mode
    ;;
  empty)
    ;;
  *)
    echo "Unsupported WIKI_SYNC_MODE: $MODE"
    exit 1
    ;;
esac

sort -u "$MANIFEST" -o "$MANIFEST"

copy_manifest_pages() {
  if [[ ! -s "$MANIFEST" ]]; then
    echo "No markdown pages selected for wiki sync"
    return 0
  fi

  echo "Copying selected markdown pages into wiki"
  while IFS=$'\t' read -r rel slug; do
    [[ -n "${rel:-}" ]] || continue
    cp -v "$rel" "$WIKI_DIR/$slug.md"
  done < "$MANIFEST"
}

write_generated_home() {
  cat > "$WIKI_DIR/Home.md" <<HOME
# ${REPO##*/}

This wiki is managed by the repository sync-wiki workflow and sync-to-wiki script.

No repository markdown source has been designated for the wiki home page yet.
HOME
}

copy_home_page() {
  if [[ -n "$HOME_SOURCE" && -f "$HOME_SOURCE" ]]; then
    cp -v "$HOME_SOURCE" "$WIKI_DIR/Home.md"
  else
    write_generated_home
  fi
}

build_sidebar() {
  local sidebar="$1"
  cat > "$sidebar" <<SIDEBAR
# Cirrus

- [Home](Home)
- [Current State](CURRENT_STATE)
- [Setup Plan](SETUP_PLAN)
- [Services](SERVICES)
- [Resume](RESUME)
- [Action Log](Action-Log)
- [Token Efficiency](docs-token-efficiency)

## Docs

SIDEBAR

  if [[ -s "$MANIFEST" ]]; then
    while IFS=$'\t' read -r rel slug; do
      [[ -n "${rel:-}" ]] || continue
      printf -- '- [%s](%s)\n' "$(sidebar_title_for "$rel")" "$slug" >> "$sidebar"
    done < "$MANIFEST"
  fi
}

rewrite_markdown_links() {
  local file="$1"
  local current_rel="$2"
  local repo_root
  repo_root="$(pwd)"
  python3 - "$file" "$current_rel" "$REPO" "$repo_root" "$MANIFEST" <<'PY'
from pathlib import Path, PurePosixPath
import re
import sys

file_path = Path(sys.argv[1])
current_rel = sys.argv[2]
repo = sys.argv[3]
repo_root = Path(sys.argv[4]).resolve()
manifest_path = Path(sys.argv[5])

slug_for = {"README.md": "Home", "Home.md": "Home"}
if manifest_path.exists():
    with manifest_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            rel, slug = line.split("\t", 1)
            slug_for[rel] = slug

current_dir = str(PurePosixPath(current_rel).parent)
if current_dir == ".":
    current_dir = ""

pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
text = file_path.read_text(encoding="utf-8")

def resolve_target(target: str) -> str:
    if re.match(r"^(?:https?:|mailto:|#)", target):
        return target

    candidate = target
    anchor = ""
    if "#" in candidate:
        candidate, anchor = candidate.split("#", 1)
        anchor = "#" + anchor

    while candidate.startswith("./"):
        candidate = candidate[2:]

    candidate_path = Path(candidate)
    if candidate_path.is_absolute():
        try:
            rel_path = candidate_path.resolve().relative_to(repo_root)
        except Exception:
            rel_path = None
        if rel_path is not None:
            rel_candidate = rel_path.as_posix()
            if rel_candidate in slug_for:
                return f"https://github.com/{repo}/wiki/{slug_for[rel_candidate]}{anchor}"
            if rel_candidate.startswith("docs/"):
                docs_candidate = rel_candidate[5:]
                if docs_candidate in slug_for:
                    return f"https://github.com/{repo}/wiki/{slug_for[docs_candidate]}{anchor}"

    if candidate.startswith("docs/"):
        candidate = candidate[5:]

    if candidate.endswith(".md"):
        if candidate.startswith("/"):
            resolved = candidate.lstrip("/")
        elif current_dir:
            resolved = str((PurePosixPath(current_dir) / candidate).as_posix())
        else:
            resolved = candidate

        resolved = str(PurePosixPath(resolved))
        if resolved in slug_for:
            return f"https://github.com/{repo}/wiki/{slug_for[resolved]}{anchor}"

        docs_resolved = str(PurePosixPath("docs") / resolved)
        if docs_resolved in slug_for:
            return f"https://github.com/{repo}/wiki/{slug_for[docs_resolved]}{anchor}"

    return target

def repl(match: re.Match[str]) -> str:
    label = match.group(1)
    target = match.group(2)
    return f"[{label}]({resolve_target(target)})"

file_path.write_text(pattern.sub(repl, text), encoding="utf-8")
PY
}

copy_manifest_pages
copy_home_page
build_sidebar "$WIKI_DIR/_Sidebar.md"

echo "Rewriting internal Markdown links for wiki page URLs"
if [[ -s "$MANIFEST" ]]; then
  while IFS=$'\t' read -r rel slug; do
    [[ -n "${rel:-}" ]] || continue
    rewrite_markdown_links "$WIKI_DIR/$slug.md" "$rel"
  done < "$MANIFEST"
fi
rewrite_markdown_links "$WIKI_DIR/Home.md" "${HOME_SOURCE:-Home.md}"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run output written to: $WIKI_DIR"
  find "$WIKI_DIR" -maxdepth 1 -type f -printf '%f\n' | sort
  exit 0
fi

cd "$WIKI_DIR"
git add --all
if git diff --cached --quiet; then
  echo "No changes to push to wiki. Exiting."
  exit 0
fi

git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" commit -m "Sync markdown -> wiki"
git push origin HEAD:master

echo "Wiki sync complete."
