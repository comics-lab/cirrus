# Token Efficiency

## Short Answer

For this project, the biggest token savings come from:

1. externalizing state into files
2. turning repeated operations into scripts
3. narrowing the active working set

Adding more agents only helps when the work is genuinely parallel and bounded. Adding skills helps when a workflow is repeated often enough to deserve a stable interface. Otherwise, both can increase token use.

## Practical Guidance

### 1. Externalize State

Keep the current truth in markdown, manifests, CSVs, and reports. Prefer files over repeated explanation.

Use files for:

- directory inventories
- file manifests
- match reports
- handoff notes
- unresolved issue lists
- canonical state snapshots

This keeps later prompts short because the model can read the file instead of being told the same story again.

### 2. Script Repeated Work

If a task happens more than once, promote it to a script.

Good candidates:

- scanning and classifying file trees
- cache building
- metadata seeding
- archive normalization
- batch promotion from audit reports
- safe cleanup passes

One reliable script is cheaper than multiple conversational reruns.

### 3. Keep The Working Set Small

Process one subtree, one publisher, or one batch at a time.

Avoid:

- “scan everything”
- overlapping batches
- re-explaining the same target directories

Small, bounded tasks reduce both token cost and failure risk.

### 4. Use Agents Selectively

Agents are useful when tasks are parallel and independent.

Good cases:

- one agent scans a library tree while another normalizes intake
- one agent builds metadata while another verifies imports

Bad cases:

- asking multiple agents to reason over the same broad context
- using agents to compensate for missing file-based state

More agents are not automatically more efficient. If the work overlaps heavily, they usually cost more tokens.

### 5. Use Skills Only For Stable Workflows

Skills are worth it only when a workflow is repeated enough to standardize.

Good skill candidates:

- host truth capture
- storage baseline checks
- library import workflow
- metadata normalization workflow

The comic-specific skill is intentionally bounded to metadata resolution and intake. It does
not replace the host, storage, or service skills, and it should not be invoked for ordinary
Docker or filesystem maintenance.

If the workflow is still changing, a script or markdown note is usually better than a skill.

### 6. Keep Output Structured

Prefer:

- CSV
- JSON
- short reports
- manifests
- checklists

Avoid turning simple state into long narrative logs unless the narrative is the actual artifact.

## Low-Token Operating Model For Cirrus

### Canonical State Files

Keep these as the primary references:

- `CURRENT_STATE.md`
- `SERVICES.md`
- `SETUP_PLAN.md`
- `Action-Log.md`
- `MISSING_ISSUES.md`
- `RESUME.md`

### Canonical Data Files

Keep these for machine-readable state:

- cache databases
- CSV reports
- JSON manifests
- extraction reports
- resolver reports

### Script Layer

Formalize scripts for:

- cache building
- series matching
- metadata seeding
- ISBN-only library metadata
- safe archive normalization
- batch promotion into Mylar import baskets

For comic parsing, prefer one inspect/resolve/materialize/promote pipeline with a saved JSON
plan over separate agents repeatedly rescanning the same archives. The plan is the handoff
between stages and is the main efficiency improvement.

### Agent Layer

Use agents only for:

- parallel scans
- bounded verification
- directory-specific work that can proceed without the rest of the tree

### Best Practice

When starting new work, prefer this order:

1. read the canonical markdown
2. inspect the relevant report or manifest
3. run the smallest script that answers the question
4. only then ask for broader interpretation

That sequence is the main token saver.

## Project-Specific Rule

If a task is likely to recur in this repo, add one of these:

- a markdown state file
- a reusable script
- a small CSV or JSON manifest

Do not default to adding another agent unless the task is clearly parallel and bounded.
