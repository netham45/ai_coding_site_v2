# CLI Surface Spec

## Purpose

This document defines the CLI surface for all readable and manageable runtime state.

Design goals:

- the same CLI serves both operators and AI sessions
- no critical runner variable is hidden
- every durable concept is queryable
- every practical database operation is exposed where sensible
- mutation commands exist where safe, otherwise read-only status is provided

---

## 1. General principles

### Rules

- every durable database concept should have a CLI read path
- every running execution cursor should have a CLI read path
- every safe operator action should have a CLI mutation path
- every AI-facing step in the command loop should have a CLI operation
- command output should support `table`, `json`, and `yaml`
- historical queries should support version/run selection where applicable

### Output conventions

- human-readable by default
- `--json` for machine parsing
- `--yaml` for config-like inspection
- `--verbose` to expose all useful columns

---

## 2. Tree and hierarchy commands

### Show node subtree

- `ai-tool tree show --node <id>`
- `ai-tool tree show --node <id> --full`
- `ai-tool tree show --node <id> --json`

### Show ancestors

- `ai-tool node ancestors --node <id>`
- `ai-tool node ancestors --node <id> --to-root --json`

### Show children

- `ai-tool node children --node <id>`
- `ai-tool node children --node <id> --versions`

### Show siblings

- `ai-tool node siblings --node <id>`

### Show version lineage

- `ai-tool node lineage --node <id>`

### Show dependency state

- `ai-tool node dependencies --node <id>`
- `ai-tool node dependency-status --node <id>`

---

## 3. Node and run state commands

### Show node summary

- `ai-tool node show --node <id>`

Should expose:

- node version ID
- logical node ID
- parent node version ID
- tier
- node kind
- status
- current branch
- seed commit
- final commit
- compiled workflow ID
- active run ID
- supersession lineage

### Show node run

- `ai-tool node run show --node <id>`
- `ai-tool node run show --run <id>`

Should expose:

- lifecycle state
- current task ID
- current compiled subtask ID
- current subtask attempt
- last completed compiled subtask ID
- execution cursor JSON
- failure counters
- resumable flag
- session binding
- pause flag state

### List node runs

- `ai-tool node runs --node <id>`

### Pause / resume / cancel

- `ai-tool node pause --node <id>`
- `ai-tool node resume --node <id>`
- `ai-tool node cancel --node <id>`

---

## 4. Workflow, task, and subtask commands

### Show compiled workflow

- `ai-tool workflow show --node <id>`
- `ai-tool workflow show --workflow <id>`

Should expose:

- source definitions used
- override files used
- hook insertions
- resolved workflow hash

### List compiled tasks

- `ai-tool task list --node <id>`
- `ai-tool task list --run <id>`

### Show current task

- `ai-tool task current --node <id>`

### List compiled subtasks

- `ai-tool subtask list --node <id>`
- `ai-tool subtask list --run <id>`

### Show current subtask

- `ai-tool subtask current --node <id>`

### Show one compiled subtask

- `ai-tool subtask show --compiled-subtask <id>`

### Show subtask attempts

- `ai-tool subtask attempts --node <id>`
- `ai-tool subtask attempts --run <id>`
- `ai-tool subtask attempts --compiled-subtask <id>`

### Show subtask logs and context

- `ai-tool subtask logs --attempt <id>`
- `ai-tool subtask context --attempt <id>`
- `ai-tool subtask output --attempt <id>`

### Retry current subtask

- `ai-tool subtask retry --node <id>`
- `ai-tool subtask retry --attempt <id>`

---

## 5. AI-facing execution loop commands

These are the commands the AI session itself should be able to use directly.

### Session bootstrap

- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

### Prompt / context retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`

### Summary/reporting

- `ai-tool summary register --node <id> --file <path> --type <type>`

### Cursor control

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session attach --node <id>`

---

## 6. YAML, overrides, and hooks commands

### Show source YAML for a node

- `ai-tool yaml show --node <id>`

### Show resolved YAML after overrides

- `ai-tool yaml resolved --node <id>`

### Show source document lineage

- `ai-tool yaml sources --node <id>`

### Validate YAML

- `ai-tool yaml validate --path <file>`
- `ai-tool yaml validate --node <id>`

### Show overrides in effect

- `ai-tool overrides list --node <id>`
- `ai-tool overrides show --node <id>`

### Show hooks in effect

- `ai-tool hooks list --node <id>`
- `ai-tool hooks show --node <id>`
- `ai-tool hooks run --node <id> --event <event>`

---

## 7. Git and rectification commands

### Show branch info

- `ai-tool git branch show --node <id>`

### Show seed and final commits

- `ai-tool git seed show --node <id>`
- `ai-tool git final show --node <id>`

### Reset and merge operations

- `ai-tool git reset-node-to-seed --node <id>`
- `ai-tool git merge-current-children --node <id> --ordered`
- `ai-tool git finalize-node --node <id>`

### Rectification

- `ai-tool node regenerate --node <id>`
- `ai-tool node rectify-upstream --node <id>`
- `ai-tool rebuild show --node <id>`

### Merge lineage

- `ai-tool merge-events show --node <id>`
- `ai-tool merge-conflicts show --node <id>`

### Merge gating

- `ai-tool merge parent --node <id>`
- `ai-tool merge base --node <id>`
- `ai-tool merge approve --node <id>`

---

## 8. Review, validation, summary, and docs commands

### Validation

- `ai-tool validation show --node <id>`
- `ai-tool validation show --run <id>`

### Review

- `ai-tool review show --node <id>`
- `ai-tool review show --run <id>`

### Summaries

- `ai-tool summary show --node <id>`
- `ai-tool summary show --run <id>`
- `ai-tool summary list --node <id>`

### Docs

- `ai-tool docs build-node-view --node <id>`
- `ai-tool docs build-tree --node <id>`
- `ai-tool docs list --node <id>`
- `ai-tool docs show --node <id> --scope local`
- `ai-tool docs show --node <id> --scope merged`

---

## 9. Prompt and provenance commands

### Prompt lineage

- `ai-tool prompts list --node <id>`
- `ai-tool prompts list --run <id>`
- `ai-tool prompts show --prompt <id>`

### Entity provenance

- `ai-tool entity show --name <canonical_name>`
- `ai-tool entity history --name <canonical_name>`
- `ai-tool entity relations --name <canonical_name>`
- `ai-tool entity changed-by --name <canonical_name>`

### Rationale

- `ai-tool rationale show --node <id>`
- `ai-tool rationale entity --name <canonical_name>`

---

## 10. Session and tmux commands

### Show sessions

- `ai-tool session show --node <id>`
- `ai-tool session show --session <id>`
- `ai-tool session list --node <id>`

### Heartbeats and events

- `ai-tool session events --session <id>`
- `ai-tool session heartbeat --session <id>`

### Attach / resume / nudge

- `ai-tool session attach --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session nudge --node <id>`

### Push/pop child sessions

- `ai-tool session push --node <id> --reason <reason>`
- `ai-tool session pop --session <id> --summary-file <path>`

These commands support the primary-session model with optional pushed child sessions for bounded research/review work.

---

## 11. Database-facing query mappings

Examples:

### `ai-tool subtask current --node <id>`
Reads from:

- `latest_node_runs`
- `node_run_state`
- `compiled_subtasks`

### `ai-tool workflow show --node <id>`
Reads from:

- `compiled_workflows`
- `compiled_workflow_sources`
- `compiled_tasks`
- `compiled_subtasks`
- `compiled_subtask_dependencies`

### `ai-tool merge-events show --node <id>`
Reads from:

- `merge_events`
- `merge_conflicts`

### `ai-tool tree show --node <id>`
Uses recursive node traversal against:

- `node_versions`

---

## 12. Read-only vs mutable surface

### Mutable where sensible

- pause node
- resume node
- retry subtask
- run hooks
- regenerate node
- rectify upstream
- finalize node
- approve merge to parent/base

### Read-only where safer

- raw prompt history
- merge history
- compiled workflow snapshots
- subtask attempt history
- session events
- documentation history

The goal is broad visibility with conservative mutation of history.

---

## 13. Final CLI rule

If a value is durable enough to influence execution, debugging, auditability, or operator decisions, there should be a CLI path to inspect it.

