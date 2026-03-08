# CLI Surface Spec V2

## Purpose

This document defines the canonical CLI surface for readable and manageable runtime state.

V2 expands the prior CLI spec by:

- aligning commands with the v2 lifecycle and runtime model
- adding clearer action coverage for automation parity
- adding stronger review/testing/docs visibility
- adding clearer session, blocker, and pause-state introspection
- clarifying which commands are read-only versus mutating

Design goals:

- the same CLI serves both operators and AI sessions
- every operationally relevant durable concept has a read path
- every safe user-visible action has an automation path
- command semantics are consistent with durable runtime ownership
- CLI access should follow the daemon authority model rather than direct operational DB coordination

---

## 1. General principles

### Rules

- every durable database concept should have a CLI read path
- every running execution cursor should have a CLI read path
- every safe operator action should have a CLI mutation path
- every AI-facing step in the command loop should have a CLI operation
- historical queries should support version/run selection where applicable
- mutating CLI commands should go through daemon/API logic rather than coordinating directly against the database

### Output conventions

- human-readable by default
- `--json` for machine parsing
- `--yaml` for config-like inspection
- `--verbose` to expose additional useful fields

### Mutation rule

If a command changes execution state, the resulting durable state must be inspectable afterward.

### Transport and auth rule

Recommended initial access model:

- CLI talks to the daemon over HTTPS
- daemon access is protected by a runtime-generated cookie
- future web/dashboard surfaces should use the same daemon-facing model

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

Should expose:

- authoritative lineage edges
- candidate lineage edges when rebuilds are in progress
- current authoritative selector for the logical node

- `ai-tool node lineage --node <id>`

### Show dependency state

- `ai-tool node dependencies --node <id>`
- `ai-tool node dependency-status --node <id>`

### Validate dependency graph

- `ai-tool node dependency-validate --node <id>`

### Show blockers

- `ai-tool node blockers --node <id>`

---

## 3. Node creation and planning commands

These commands strengthen automation parity for user-visible planning actions.

### Create top-level node

- `ai-tool node create --kind <kind> --title <title> --file <path>`

### Create child node manually

- `ai-tool node child create --parent <id> --kind <kind> --title <title> --file <path>`

### Generate layout

- `ai-tool layout generate --node <id>`

### Show layout

- `ai-tool layout show --node <id>`

### Update layout

- `ai-tool layout update --node <id> --file <path>`

### Validate layout

- `ai-tool layout validate --node <id>`

These command names are suggested, not frozen, but the capability should exist.

---

## 4. Node and run state commands

### Show node summary

- `ai-tool node show --node <id>`

Should expose:

- node version ID
- logical node ID
- parent node version ID
- tier
- node kind
- lifecycle status
- branch
- seed commit
- final commit
- compiled workflow ID
- active run ID
- supersession lineage
- authoritative vs candidate status when superseding rebuilds are in progress
- authoritative node version ID for the logical node
- latest created node version ID for the logical node if different

### Show node run

- `ai-tool node run show --node <id>`
- `ai-tool node run show --run <id>`

Should expose:

- run status
- lifecycle state
- current task ID
- current compiled subtask ID
- current attempt number
- last completed compiled subtask ID
- pause flag
- resumable flag
- active primary session binding derived from session state

### Start or admit a run

- `ai-tool node run start --node <id>`

### List node runs

- `ai-tool node runs --node <id>`

### Pause, resume, cancel

- `ai-tool node pause --node <id>`
- `ai-tool node resume --node <id>`
- `ai-tool node cancel --node <id>`

### Show pause state

- `ai-tool node pause-state --node <id>`

### Show decision history

- `ai-tool node decision-history --node <id>`

### Show node event history

- `ai-tool node events --node <id>`
- `ai-tool node events --run <id>`

Should expose at minimum:

- pause events
- recovery events
- parent decision events
- cutover events

---

## 5. Workflow, task, and subtask commands

### Show compiled workflow

- `ai-tool workflow show --node <id>`
- `ai-tool workflow show --workflow <id>`

Should expose:

- source definitions used
- overrides used
- hooks inserted
- resolved workflow hash
- built-in library version used for compilation
- override compatibility warnings if any

### Show compiled subtask chain

- `ai-tool workflow chain --node <id>`
- `ai-tool workflow chain --node <id> --run <id>`
- `ai-tool workflow chain --workflow <id>`

Should expose:

- ordered compiled subtask chain for the selected workflow
- compiled subtask ID, ordinal, type, and label/title
- dependency edges or wait semantics between compiled subtasks where applicable
- structure-only output when no run is selected
- run-aware state when a run is selected or an active run exists

When run-aware state is shown, each compiled subtask should expose at minimum:

- derived execution state such as `pending`, `current`, `complete`, `paused`, `failed`, or `skipped`
- latest attempt number if any
- latest attempt status if any
- whether the subtask is the current cursor target
- latest summary, pause flag, or failure class reference if present
- blocker or gate explanation if the subtask is waiting on an explicit gate

### Show current workflow binding

- `ai-tool workflow current --node <id>`

### Show workflow source lineage

- `ai-tool workflow sources --node <id>`
- `ai-tool workflow sources --workflow <id>`

### Compile or recompile workflow

- `ai-tool workflow compile --node <id>`

This is the canonical mutation path for:

- first compile of an existing draft node version
- recompile after layout, policy, hook, or override changes
- reattempt after a durable compile failure

Recommended behavior:

- compile against the current authoritative source set for the selected node version
- persist either a compiled workflow snapshot or a compile-failure record
- update lifecycle visibility accordingly
- refuse run admission until compilation succeeds

### Show compile failures

- `ai-tool workflow compile-failures --node <id>`
- `ai-tool workflow compile-failures --workflow <id>`

### Advance, pause, resume workflow

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`

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

### Show compiled subtask

- `ai-tool subtask show --compiled-subtask <id>`

### Show subtask attempts

- `ai-tool subtask attempts --node <id>`
- `ai-tool subtask attempts --run <id>`
- `ai-tool subtask attempts --compiled-subtask <id>`

### Show subtask logs, context, output

- `ai-tool subtask logs --attempt <id>`
- `ai-tool subtask context --attempt <id>`
- `ai-tool subtask output --attempt <id>`

### Retry current subtask

- `ai-tool subtask retry --node <id>`
- `ai-tool subtask retry --attempt <id>`

---

## 6. AI-facing execution loop commands

These are the commands the AI session itself should be able to use directly.

### Session bootstrap

- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

### Prompt and context retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`

### Summary registration

- `ai-tool summary register --node <id> --file <path> --type <type>`

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session attach --node <id>`

Rule:

- AI-facing commands should be sufficient for the session to retrieve work, report progress, and recover from interruption without hidden runtime-only state.

---

## 7. Review, validation, testing, and docs commands

V2 makes these quality-gate families more explicit.

### Validation

- `ai-tool validation show --node <id>`
- `ai-tool validation show --run <id>`
- `ai-tool validation results --node <id>`

### Review

- `ai-tool review show --node <id>`
- `ai-tool review show --run <id>`
- `ai-tool review results --node <id>`
- `ai-tool review run --node <id> --scope <scope>`

### Testing

- `ai-tool testing show --node <id>`
- `ai-tool testing show --run <id>`
- `ai-tool testing results --node <id>`
- `ai-tool testing run --node <id>`

### Docs

- `ai-tool docs build-node-view --node <id>`
- `ai-tool docs build-tree --node <id>`
- `ai-tool docs list --node <id>`
- `ai-tool docs show --node <id> --scope local`
- `ai-tool docs show --node <id> --scope merged`

---

## 8. YAML, overrides, and hooks commands

### Show source YAML

- `ai-tool yaml show --node <id>`

### Show resolved YAML

- `ai-tool yaml resolved --node <id>`

### Show source document lineage

- `ai-tool yaml sources --node <id>`

### Validate YAML

- `ai-tool yaml validate --path <file>`
- `ai-tool yaml validate --node <id>`

### Show compile failures

- `ai-tool workflow compile-status --node <id>`
- `ai-tool workflow compile-failures --node <id>`
- `ai-tool workflow compile-check --node <id>`

### Compile or recompile

- `ai-tool workflow compile --node <id>`

### Show overrides

- `ai-tool overrides list --node <id>`
- `ai-tool overrides show --node <id>`

### Show hooks

- `ai-tool hooks list --node <id>`
- `ai-tool hooks show --node <id>`

### Run hooks

- `ai-tool hooks run --node <id> --event <event>`

### Update policy or override

- `ai-tool policy update --file <path>`

This capability may be implemented differently, but a CLI-driven automation path should exist.

---

## 9. Git and rectification commands

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

## 10. Prompt, summary, rationale, and provenance commands

### Prompt lineage

- `ai-tool prompts list --node <id>`
- `ai-tool prompts list --run <id>`
- `ai-tool prompts show --prompt <id>`

### Summaries

- `ai-tool summary show --node <id>`
- `ai-tool summary show --run <id>`
- `ai-tool summary list --node <id>`

### Rationale

- `ai-tool rationale show --node <id>`
- `ai-tool rationale entity --name <canonical_name>`

### Entity provenance

- `ai-tool entity show --name <canonical_name>`
- `ai-tool entity history --name <canonical_name>`
- `ai-tool entity relations --name <canonical_name>`
- `ai-tool entity changed-by --name <canonical_name>`

---

## 11. Session and tmux commands

### Show sessions

- `ai-tool session show --node <id>`
- `ai-tool session show --session <id>`
- `ai-tool session list --node <id>`

### Heartbeats and events

- `ai-tool session events --session <id>`
- `ai-tool session heartbeat --session <id>`

### Attach, resume, nudge

- `ai-tool session attach --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session nudge --node <id>`

### Push/pop child sessions

- `ai-tool session push --node <id> --reason <reason>`
- `ai-tool session pop --session <id> --summary-file <path>`

### Child-session results

- `ai-tool session result show --session <id>`

### Workflow events

- `ai-tool workflow events --node <id>`
- `ai-tool workflow events --run <id>`

---

## 12. Read-only versus mutable surfaces

### Mutable where sensible

- create nodes
- create child nodes
- update layouts
- validate and start runs
- pause/resume/cancel nodes
- retry subtasks
- run hooks where allowed
- regenerate nodes
- rectify upstream
- finalize nodes
- approve gated merges
- run explicit review/testing/docs actions where policy allows

### Read-only where safer

- prompt history
- summary history
- merge history
- compiled workflow snapshots
- subtask attempt history
- session event history
- docs history
- provenance history

The system should prefer visibility broadly and mutation conservatively.

---

## 13. Database-facing query mappings

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

### `ai-tool review show --node <id>`

Reads from:

- `review_results`
- `summaries`

### `ai-tool testing show --node <id>`

Reads from:

- `test_results`
- `summaries`

### `ai-tool merge-events show --node <id>`

Reads from:

- `merge_events`
- `merge_conflicts`

### `ai-tool tree show --node <id>`

Uses recursive traversal against:

- `node_versions`
- `node_children`

---

## 14. CLI completeness rule

If a value is durable enough to influence:

- execution
- debugging
- auditability
- operator decisions
- AI-session decisions

then there should be a CLI path to inspect it.

If a user-visible action exists in the interface, there should be an automatable CLI path for it unless the design explicitly rejects that action from automation.

---

## 15. V2 closure notes

This V2 CLI spec resolves or reduces the following prior gaps:

- better automation parity for planning/editing actions
- clearer review/testing/docs CLI surfaces
- clearer blocker and pause-state introspection
- clearer read-only versus mutation boundaries

Remaining follow-on work still needed:

- confirm final command naming and grouping
- finalize which workflow-event and decision-history surfaces ship in the first implementation slice
- align implementation slicing with this command surface
