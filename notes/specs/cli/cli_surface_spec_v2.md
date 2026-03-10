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

Implementation staging note:

- `tree show --node <id>` is now implemented as a daemon-backed flattened subtree view with `depth`, hierarchy identity, and live lifecycle/run status per node
- `tree show --node <id> --full` is now accepted as an operator alias for the same full flattened subtree payload; the CLI marks the returned payload with `full_view = true`

### Show ancestors

- `ai-tool node ancestors --node <id>`
- `ai-tool node ancestors --node <id> --to-root --json`

Implementation staging note:

- `node ancestors --node <id> --to-root` is now accepted explicitly; the current daemon read already returns the full durable ancestor chain to root, so the flag is presently a no-op selector surfaced in CLI output

### Show children

- `ai-tool node children --node <id>`
- `ai-tool node children --node <id> --versions`

Implementation staging note:

- `node children --node <id>` continues to read the durable hierarchy children directly
- `node children --node <id> --versions` now enriches each child row with the daemon-backed operator summary so version selectors and current run/lifecycle state are visible in one command

### Show child materialization and scheduling

- `ai-tool node child-materialization --node <id>`
- `ai-tool node child-results --node <id>`
- `ai-tool node reconcile --node <id>`

Should expose:

- parent authoritative node version id
- layout source path and hash
- authority mode
- materialization status
- per-child `layout_child_id`
- lifecycle state and current scheduling classification

Implementation staging note:

- `node child-materialization --node <id>` is now implemented as a daemon-backed read of the current layout-materialization state
- `node materialize-children --node <id>` is now the explicit mutation path for default built-in layout materialization
- `node child-reconciliation --node <id>` now exposes the current manual/layout authority mode, available reconciliation decisions, and child-origin counts
- `node reconcile-children --node <id> --decision preserve_manual` now performs the currently supported explicit hybrid-reconciliation mutation
- `node child-results --node <id>` now exposes authoritative child finals, deterministic merge order, and blocked-child classification for the current parent version
- `node reconcile --node <id>` now exposes the staged parent-local reconcile prompt and the current derived reconcile context

### Show siblings

- `ai-tool node siblings --node <id>`

Implementation staging note:

- `node siblings --node <id>` is now implemented as a daemon-backed operator summary list for sibling nodes

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
- `ai-tool workflow start --kind <kind> --prompt <prompt>`

Implementation staging note:

- `workflow start --kind <kind> --prompt <prompt> [--title <title>] [--no-run]` is now the daemon-backed top-level creation surface
- it creates a parentless node, captures source lineage, compiles the initial workflow, transitions the node to `READY`, and starts the first run unless `--no-run` is supplied
- `node create --kind <kind> --title <title> --prompt <prompt> --compile [--start-run]` is now the equivalent top-level node-creation path for operators who prefer the `node` namespace
- these create-on-start surfaces are intentionally limited to top-level kinds; parented manual creation still uses `node create --parent ...` or `node child create ...`

### Create child node manually

- `ai-tool node child create --parent <id> --kind <kind> --title <title> --file <path>`

Implementation staging note:

- `node child create --parent <id> --kind <kind> --title <title> --prompt <text>` is now implemented as the explicit manual child-construction path
- the existing `node create --parent <id> ...` path now uses the same daemon-side manual-authority bookkeeping

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

Implementation staging note:

- `node show --node <id>` is now implemented as an aggregated operator summary combining hierarchy identity, lifecycle state, current run/subtask pointers, current authoritative/current-version ids, and branch metadata

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

Implementation staging note:

- `node cancel --node <id>` and the alias `workflow cancel --node <id>` are now implemented as daemon-backed run-control mutations
- successful cancellation now records both daemon authority mutation history and workflow-event history before the lifecycle settles at `CANCELLED`
- repeated cancel calls on already cancelled or non-active nodes still fail with a structured CLI error rather than silently succeeding

### Show pause state

- `ai-tool node pause-state --node <id>`
- `ai-tool node approve --node <id> --pause-flag <flag>`
- `ai-tool workflow approve --node <id> --pause-flag <flag>`
- `ai-tool node interventions --node <id>`
- `ai-tool node intervention-apply --node <id> --kind <kind> --action <action>`

Implementation staging note:

- `node pause-state --node <id>` is now implemented as a focused view over the durable lifecycle row for the node
- `node approve --node <id>` and `workflow approve --node <id>` now mark the active pause flag approved without resuming yet
- `workflow resume --node <id>` still targets `/api/nodes/resume`, but resume now rejects unapproved non-manual pause flags with a structured conflict payload
- `node interventions --node <id>` now exposes the current bounded unified intervention catalog for pause approval, child reconciliation, merge conflict, session recovery, and blocked cutover attention
- `node intervention-apply --node <id> --kind <kind> --action <action>` now routes the currently supported intervention mutations through one explicit daemon-owned command instead of separate ad hoc paths
- the current apply surface supports:
  - `pause_approval -> approve_pause`
  - `child_reconciliation -> preserve_manual`
  - `merge_conflict -> abort_merge|resolve_conflict`
  - `session_recovery -> resume_session`
- blocked cutover is currently read-only on this surface and rebuild-specific intervention actions remain deferred

### Show decision history

- `ai-tool node decision-history --node <id>`
- `ai-tool node child-failures --node <id>`
- `ai-tool node respond-to-child-failure --node <id> --child <child_id> [--action retry_child|regenerate_child|replan_parent|pause_for_user]`
- `ai-tool node quality-chain --node <id>`

### Show node event history

- `ai-tool node events --node <id>`
- `ai-tool node events --run <id>`

Should expose at minimum:

- pause events
- recovery events
- parent decision events
- cutover events

Implementation staging note:

- `node events --node <id>` is now implemented as a combined operator view over `daemon_mutation_events` and bounded `workflow_events`, with `event_scope` distinguishing authority vs pause history
- `node events --run <id>` remains deferred until the broader event-history families land
- `node child-failures --node <id>` now reads the durable per-child counters for the latest parent run
- `node decision-history --node <id>` now reads `workflow_events` filtered to `event_scope = parent_decision`
- `node respond-to-child-failure --node <id> --child <child_id>` now applies the daemon-owned parent decision algorithm and supports explicit operator override via `--action`
- parent failure reads now expose the expanded matrix detail, including `failure_origin`, `decision_reason`, `options_considered`, threshold triggers, and the frozen threshold policy used for the decision
- `node quality-chain --node <id>` now runs the built-in validation, review, testing, provenance, docs, and final-summary path as one daemon-owned late-chain command once the active run has reached its quality stages

### Show audit bundle

- `ai-tool node audit --node <id>`
- `ai-tool node run audit --node <id>`
- `ai-tool node run audit --run <id>`

Should expose at minimum:

- the current node operator summary
- authoritative lineage and authoritative version selection
- current compiled workflow and workflow chain when available
- source lineage and compile failures
- prompt and summary history
- validation, review, and testing result history
- session history with session-event history
- rebuild, merge, and documentation history
- run-scoped attempt, prompt, summary, and session records for historical runs

Implementation staging note:

- `node audit --node <id>` is now implemented as a daemon-backed aggregated reconstruction view over the existing durable history tables and read models
- `node run audit --node <id>` resolves to the latest run for the node, while `node run audit --run <id>` targets a specific historical run directly
- these audit commands are intentionally aggregation surfaces only; they do not introduce a second source of truth beyond the underlying durable tables
- run-scoped `workflow_events` may legitimately be empty for runs that never hit a pause, approval, retry, cancel, parent-decision, or other evented workflow-control path

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

Implementation staging note:

- `workflow chain --node <id>` now exposes derived execution state, latest-attempt number/status, current-cursor identity, latest summary, and pause-flag visibility when an active run exists for the workflow

### Show current workflow binding

- `ai-tool workflow current --node <id>`

### Show workflow source lineage

- `ai-tool workflow sources --node <id>`
- `ai-tool workflow sources --workflow <id>`

Implementation staging note:

- the current implementation supports both `workflow sources --node <id>` and `workflow sources --workflow <id>` against persisted compiled workflow lineage
- `node sources --node <id>` remains the authoritative inspection path for pre-compile node-version source capture

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

Implementation staging note:

- the first implementation slice compiles a deterministic linear chain with one compiled subtask per resolved task definition
- richer override resolution, hook insertion, and rendered multi-subtask expansion remain later compiler stages

### Show compile failures

- `ai-tool workflow compile-failures --node <id>`
- `ai-tool workflow compile-failures --workflow <id>`

### Advance, pause, resume workflow

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`

Implementation staging note:

- `workflow advance --node <id>` is now implemented as a daemon-backed durable cursor transition over `node_run_state`
- pause and resume now also synchronize the durable run state for the active run

### List compiled tasks

- `ai-tool task list --node <id>`
- `ai-tool task list --run <id>`

Implementation staging note:

- `task list --node <id>` is now implemented as a CLI projection over the current compiled workflow plus durable lifecycle state, returning compiled tasks with `subtask_count` and `is_current`
- run-targeted task listing remains deferred until a dedicated run-scoped workflow read is added

### Show current task

- `ai-tool task current --node <id>`

Implementation staging note:

- `task current --node <id>` is now implemented as a CLI projection over the current compiled workflow plus durable lifecycle state, returning the current compiled task and current compiled subtask selector

### List compiled subtasks

- `ai-tool subtask list --node <id>`
- `ai-tool subtask list --run <id>`

Implementation staging note:

- `subtask list --node <id>` is now implemented as a flattened projection of the current compiled workflow plus durable lifecycle state, with `task_key`, `task_ordinal`, and `is_current` on each subtask row
- run-targeted subtask listing remains deferred until a dedicated run-scoped workflow read is added

### Show current subtask

- `ai-tool subtask current --node <id>`

Implementation staging note:

- the current implementation returns the active run snapshot, live cursor state, current compiled subtask payload, and latest attempt payload in one response envelope

### Show compiled subtask

- `ai-tool subtask show --compiled-subtask <id>`

### Show subtask attempts

- `ai-tool subtask attempts --node <id>`
- `ai-tool subtask attempts --run <id>`
- `ai-tool subtask attempts --compiled-subtask <id>`
- `ai-tool subtask attempt-show --attempt <id>`

Implementation staging note:

- the current implementation now supports daemon-backed attempt history by node through `subtask attempts --node <id>` and single-attempt inspection through `subtask attempt-show --attempt <id>`
- run-targeted and compiled-subtask-targeted attempt listing remain deferred until a dedicated run-scoped attempt catalog is added
- `subtask current` and mutation responses still mirror the latest attempt inline for compatibility, but they are no longer the only attempt-inspection surface

### Show subtask logs, context, output

- `ai-tool subtask logs --attempt <id>`
- `ai-tool subtask context --attempt <id>`
- `ai-tool subtask output --attempt <id>`

### Retry current subtask

- `ai-tool subtask retry --node <id>`
- `ai-tool subtask retry --attempt <id>`

Implementation staging note:

- `subtask retry --node <id>` now retries the current failed or retry-pending subtask on the latest retryable run for the node
- `subtask retry --attempt <id>` now resolves the owning run from the supplied attempt and starts a new durable attempt on the same compiled subtask
- retry requests now return a structured conflict error when the targeted subtask already has a running attempt

---

## 6. AI-facing execution loop commands

These are the commands the AI session itself should be able to use directly.

### Session bootstrap

- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

Implementation staging note:

- `session show-current` now exposes the durable logical-node binding directly, including `logical_node_id`, `node_kind`, `node_title`, and current `run_status`, so an AI session can discover the exact bound node before issuing `workflow current` or `subtask ...` lookups
- the same response now also carries `recovery_classification`, allowing bootstrap code to distinguish healthy vs stale-but-recoverable primary sessions without a separate recovery-status round trip

### Prompt and context retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`
- `ai-tool subtask environment --node <id>`

Implementation staging note:

- `subtask prompt` and `subtask context` are now real daemon-backed commands
- `subtask prompt` returns the frozen compiled prompt payload for the current compiled subtask and now includes a durable `prompt_id`
- `subtask context` returns the durable current-attempt context when an attempt exists, otherwise it returns the synthesized current subtask input snapshot
- both surfaces now also expose `stage_context_json`, the daemon-assembled stage-start bundle built from durable startup metadata, stage metadata, dependency state, recent prompt/summary history, and cursor-carried child/reconcile context
- the same `stage_context_json` bundle is also embedded into the compatibility `input_context_json` payload returned by `subtask context` so prompt-first and context-first clients see the same startup contract
- current startup metadata includes the node prompt, title, node kind, run number, trigger reason, and compiled workflow identity for the active run
- current stage metadata includes the compiled task/subtask identity, source subtask key, subtask type, and frozen environment request metadata for the active compiled subtask
- `subtask environment` now returns the current compiled subtask's frozen `environment_policy_ref` and `environment_request`
- `prompts history --node <id>` and `prompts delivered-show --prompt <id>` now expose durable prompt-delivery history without changing the packaged-asset `prompts show` command

### Environment policy inspection

- `ai-tool environment policies`
- `ai-tool environment show --attempt <id>`

Implementation staging note:

- `environment policies` now lists built-in and project environment policy documents with declared-profile visibility
- `environment show --attempt <id>` now returns the durable `execution_environment_json` captured when the attempt was started

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id> --result-file result.json`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`
- `ai-tool subtask fail --compiled-subtask <id> --result-file result.json`

Implementation staging note:

- `subtask fail` now accepts the documented `--summary-file <path>` contract on the CLI and still allows the existing inline `--summary` compatibility path
- the CLI reads the failure summary file locally and sends the content to the daemon as the durable failure summary
- `subtask complete` and `subtask fail` now also accept `--result-file <path>`; the CLI reads JSON locally and sends it as the explicit execution-result payload for the attempt
- the daemon persists that explicit payload in `execution_result_json` and mirrors it into `output_json` for compatibility with already-implemented validation, review, testing, and history logic
- this slice still does not make ordinary shell or tool execution daemon-owned; it makes session-reported execution results explicit and durably inspectable
- `subtask heartbeat` is now implemented as a durable update on the active attempt and run cursor metadata, not yet as a dedicated heartbeat-history table

### Summary registration

- `ai-tool summary register --node <id> --file <path> --type <type>`

Implementation staging note:

- `summary register` now writes a durable summary-history row and returns a stable `summary_id`
- the active subtask attempt still mirrors `registered_summaries` for compatibility with existing validation and runtime surfaces
- `summary history --node <id>` and `summary show --summary <id>` now expose durable summary retrieval

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session provider-resume --node <id>`
- `ai-tool session attach --node <id>`

Rule:

- AI-facing commands should be sufficient for the session to retrieve work, report progress, and recover from interruption without hidden runtime-only state.

Implementation staging note:

- `workflow pause --node <id>` and `workflow resume --node <id>` now exist as AI-facing aliases over the same daemon-controlled pause/resume mutations used by operator flows

---

## 7. Review, validation, testing, and docs commands

V2 makes these quality-gate families more explicit.

### Validation

- `ai-tool validation show --node <id>`
- `ai-tool validation show --run <id>`
- `ai-tool validation results --node <id>`

Implementation note: the current CLI also exposes `node validate --node <id>` as a direct alias over the daemon's current validation gate evaluator for the active run.

### Review

- `ai-tool review show --node <id>`
- `ai-tool review show --run <id>`
- `ai-tool review results --node <id>`
- `ai-tool review run --node <id> --status <pass|revise|fail>`

Implementation note: the current CLI now exposes `review run --node <id> --status ...` plus optional `--summary`, `--findings-file`, and `--criteria-file` payloads so the active review subtask can record a structured outcome and let the daemon route pass/revise/fail behavior in one command. `node review --node <id> ...` is an alias over the same daemon path.

### Testing

- `ai-tool testing show --node <id>`
- `ai-tool testing show --run <id>`
- `ai-tool testing results --node <id>`
- `ai-tool testing run --node <id>`

Implementation note: the current CLI now exposes `testing show`, `testing results`, and `testing run` as daemon-backed testing-gate surfaces, and `node test --node <id>` is an alias over the same evaluator for the active `run_tests` subtask.

### Docs

- `ai-tool docs build-node-view --node <id>`
- `ai-tool docs build-tree --node <id>`
- `ai-tool docs list --node <id>`
- `ai-tool docs show --node <id> --scope local`
- `ai-tool docs show --node <id> --scope merged`

Implementation note: the current CLI now exposes daemon-backed documentation generation and inspection surfaces. `docs build-node-view` materializes the canonical local/entity-history/custom views for the authoritative node version, `docs build-tree` materializes the canonical merged/rationale/custom tree views, `docs list` returns the durable output catalog for the authoritative version, and `docs show` returns the latest persisted output for the requested scope.

---

## 8. YAML, overrides, and hooks commands

### Show source YAML

- `ai-tool yaml show --node <id>`

### Show resolved YAML

- `ai-tool yaml resolved --node <id>`
- `ai-tool yaml resolved --workflow <id>`

### Show source document lineage

- `ai-tool yaml sources --node <id>`
- `ai-tool yaml sources --workflow <id>`

Implementation note: `yaml sources --node <id>` now returns the daemon-backed authoritative source-lineage bundle for the node's current authoritative version, `yaml sources --workflow <id>` returns the daemon-backed compiled-workflow source bundle, and `yaml sources --scope <scope>` remains the local packaged-resource inventory fallback for root inspection.

### Validate YAML

- `ai-tool yaml validate --path <file>`
- `ai-tool yaml validate --node <id>`

### Show compile failures

- `ai-tool workflow compile-status --node <id>`
- `ai-tool workflow compile-failures --node <id>`
- `ai-tool workflow compile-check --node <id>`

### Show compile source discovery

- `ai-tool workflow source-discovery --node <id>`
- `ai-tool workflow source-discovery --workflow <id>`

Implementation note: this stage-inspection surface now exposes the deterministic compile input order plus the resolved-document inventory that fed the compiled workflow, so source-load behavior is inspectable without opening the full compiled payload.

### Show compile schema validation

- `ai-tool workflow schema-validation --node <id>`
- `ai-tool workflow schema-validation --workflow <id>`

Implementation note: this stage-inspection surface now summarizes the YAML-family documents that passed the compile-time schema gate for a compiled workflow, grouped by family and returned in deterministic source order.

### Compile or recompile

- `ai-tool workflow compile --node <id>`

### Show overrides

- `ai-tool yaml override-chain --node <id>`
- `ai-tool yaml override-chain --workflow <id>`
- `ai-tool workflow override-resolution --node <id>`
- `ai-tool workflow override-resolution --workflow <id>`

Implementation staging note:

- the current CLI surfaces expose applied override files and resolved merged documents through the `yaml` command group rather than a separate top-level `overrides` namespace
- `workflow override-resolution` now provides the compiler-stage view of the same override fold, including applied-override counts, warnings, and resolved-document inventory
- standalone local-file diff commands remain deferred until a later override tooling slice

### Show hooks

- `ai-tool hooks list --node <id>`
- `ai-tool hooks show --node <id>`
- `ai-tool workflow hook-policy --node <id>`
- `ai-tool workflow hook-policy --workflow <id>`

Implementation staging note:

- the current implementation exposes compiled hook inspection as `ai-tool workflow hooks --node <id>` or `ai-tool workflow hooks --workflow <id>`
- this surface returns selected hooks, skipped hooks, and the concrete hook-expanded subtask steps from the compiled workflow snapshot
- `workflow hook-policy` is the explicit compiler-stage view, adding the frozen `effective_policy` and `policy_impact` payloads that shaped hook expansion

### Show rendering and frozen compiled payloads

- `ai-tool workflow rendering --node <id>`
- `ai-tool workflow rendering --workflow <id>`

Implementation note: this stage-inspection surface returns the frozen compile-time rendering payload, including canonical rendering syntax, legacy-compatibility posture, and the rendered payload snapshot stored for each compiled subtask.

### Run hooks

- `ai-tool hooks run --node <id> --event <event>`

### Update policy or override

- `ai-tool policy update --file <path>`

This capability may be implemented differently, but a CLI-driven automation path should exist.

---

## 9. Git and rectification commands

### Show branch info

- `ai-tool git branch show --node <id>`
- `ai-tool git branch show --version <id>`

### Show seed and final commits

- `ai-tool git seed show --node <id>`
- `ai-tool git seed show --version <id>`
- `ai-tool git final show --node <id>`
- `ai-tool git final show --version <id>`

### Reset and merge operations

- `ai-tool git reset-node-to-seed --node <id>`
- `ai-tool git merge-current-children --node <id> --ordered`
- `ai-tool git finalize-node --node <id>`
- `ai-tool git bootstrap-node --version <id> [--base-version <id>] [--files-file <path>] [--replace-existing]`

Implementation staging note:

- the current implementation slice now ships both the read-side git inspection commands and the live git mutation surfaces for bootstrap, merge, abort-merge, and finalize
- `ai-tool git bootstrap-node --version <id>` creates or recreates the daemon-owned per-version live git repo
- when `--base-version <id>` is supplied, bootstrap seeds the repo from that parent version's recorded seed commit
- when `--files-file <path>` is supplied, the JSON payload must map relative file paths to file contents for the seed commit
- `ai-tool git merge-children --node <id>` shells out to real git fetch/merge across the per-version runtime repos and records durable `merge_events` and `merge_conflicts`
- `ai-tool git abort-merge --node <id>` restores the authoritative parent repo back to its recorded seed commit
- `ai-tool git finalize-node --node <id>` creates a real finalize commit and records the resulting `final_commit_sha`
- rebuild/cutover coordination is now explicitly inspectable before mutation through:
  - `node rebuild-coordination --node <id> --scope subtree|upstream`
  - `node version cutover-readiness --version <id>`

### Rectification

- `ai-tool node regenerate --node <id>`
- `ai-tool node rectify-upstream --node <id>`
- `ai-tool rebuild show --node <id>`

Implementation staging note:

- `rebuild show --node <id>` is now a real read alias over `node rebuild-history --node <id>` so rebuild inspection has both the historical and top-level operator entry points

### Merge lineage

- `ai-tool merge-events show --node <id>`
- `ai-tool merge-conflicts show --node <id>`

Implementation staging note:

- the current implementation exposes these surfaces under the existing `git` namespace as `git merge-events show --node <id>` and `git merge-conflicts show --node|--version ...`
- `git merge-conflicts record ...` and `git merge-conflicts resolve ...` are now the explicit operator paths for durable conflict halt/resume handling ahead of automated merge execution

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

Implementation staging note:

- the current CLI surface is `rationale show --node <id>` and returns the authoritative node-version rationale summary plus the recorded entity-change history for that node

### Entity provenance

- `ai-tool entity show --name <canonical_name>`
- `ai-tool entity history --name <canonical_name>`
- `ai-tool entity relations --name <canonical_name>`
- `ai-tool entity changed-by --name <canonical_name>`

Implementation staging note:

- the current CLI surface is implemented as `entity show`, `entity history`, `entity relations`, and `entity changed-by`
- `entity changed-by` is currently the changed-only view over the same durable `node_entity_changes` history rather than a separate schema family
- `node provenance-refresh --node <id>` is the daemon-backed mutation that refreshes durable provenance for the authoritative node version before those read surfaces are queried
- the current multilanguage slice keeps the same CLI shape while expanding extraction to Python plus JavaScript/TypeScript implementation code
- richer provenance entity families such as endpoints, tests, and types remain deferred, so these commands still query the current shared `module|class|function|method` model

---

## 11. Session and tmux commands

### Show sessions

- `ai-tool session show --node <id>`
- `ai-tool session show --session <id>`
- `ai-tool session list --node <id>`

Implementation staging note:

- `session show --node <id>`, `session show --session <id>`, and `session list --node <id>` are now implemented as daemon-backed reads over the durable `sessions` table plus current harness state
- those responses now include the persisted provider session id, working directory, tmux-existence flag, and tmux attach command when the backend is concrete `tmux`

### Heartbeats and events

- `ai-tool session events --session <id>`
- `ai-tool session heartbeat --session <id>`

Implementation staging note:

- `session events --session <id>` is now implemented against the durable `session_events` log
- `session heartbeat --session <id>` remains deferred; the current implementation only updates session freshness through bind/attach/resume flows

### Attach, resume, nudge

- `ai-tool session attach --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session recover --node <id>`
- `ai-tool session provider-resume --node <id>`
- `ai-tool session nudge --node <id>`
- `ai-tool node recovery-status --node <id>`
- `ai-tool node recovery-provider-status --node <id>`

Implementation staging note:

- `session attach --node <id>` still reuses the durable primary session when its harness session still exists
- `session resume --node <id>` and `session recover --node <id>` now run the provider-agnostic recovery classifier and return a structured recovery result
- `node recovery-provider-status --node <id>` now exposes provider-aware restoration details such as provider session existence, provider rebind possibility, and provider-specific next action
- `session provider-resume --node <id>` now attempts provider-aware rebound first and only falls back to provider-agnostic recovery when direct provider restoration is unavailable
- `session nudge --node <id>` now performs daemon-owned idle inspection and returns a structured nudge/escalation result
- `node recovery-status --node <id>` now shows the daemon's current recovery classification and recommended action
- `session show --node <id>`, `session show --session <id>`, and `session show-current` now also include the daemon's `recommended_action` whenever the row represents a primary session bound to an active run, so the control surface is directly actionable without forcing a separate recovery-status lookup
- if the durable primary session exists but the harness session is gone, recovery preserves the old session row as `LOST` and creates a replacement durable primary session
- if the durable tmux pointer is stale but the persisted provider session still exists on the current backend, provider-aware recovery now rebinds the existing durable session instead of creating a replacement
- if the run is marked non-resumable, recovery is rejected without creating a new session
- if duplicate active primary sessions are detected, recovery pauses for user instead of guessing ownership
- `session bind --node <id>` and `session attach --node <id>` now also reject duplicate active primary-session rows instead of silently reusing an arbitrary record
- idle nudges are suppressed while alt-screen content is active and escalate into `node pause-state` visibility when the nudge budget is exhausted
- if idle escalation pauses the run, the same durable pause-state and pause-event surfaces are used as for manual and gated pauses

### Push/pop child sessions

- `ai-tool session push --node <id> --reason <reason>`
- `ai-tool session pop --session <id> --file <path>`

Implementation staging note:

- `session push --node <id> --reason <reason>` now launches a bounded delegated child session linked to the current primary session
- `session pop --session <id> --file <path>` now validates and persists a structured JSON merge-back artifact instead of a summary-only text payload

### Child-session results

- `ai-tool session result show --session <id>`

Implementation staging note:

- `session result show --session <id>` now reads the latest durable `child_session_results` payload for that child session

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

Implementation staging note:

- prompt and summary history are now daemon-backed read-only surfaces, exposed via `prompts history`, `prompts delivered-show`, `summary history`, and `summary show`

---

## 13. Database-facing query mappings

Examples:

### `ai-tool subtask current --node <id>`

Reads from:

- `latest_node_runs`
- `node_run_state`
- `compiled_subtasks`

Implementation staging note:

- the current implementation resolves this through the active durable run for the authoritative node version, backed by `node_runs`, `node_run_state`, `compiled_tasks`, `compiled_subtasks`, and the latest matching `subtask_attempts` row

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
Implementation note: the CLI now exposes `node regenerate --node <id>`, `node rectify-upstream --node <id>`, and `node rebuild-history --node <id>` against the daemon-backed rebuild history surface.
## Implementation Note: Candidate And Rebuild Compile Variants

- workflow compile and compile-stage inspection commands now support `--version <node_version_id>` in addition to the existing authoritative `--node` target
- this makes candidate-version compile and rebuild-candidate compile explicit operator workflows instead of implicit internal-only paths
- version-targeted workflow payloads now include `compile_context` with:
  - `compile_variant`
  - `version_status`
  - rebuild metadata when the version belongs to a rebuild lineage
- compile-stage reads remain backed by the persisted compiled workflow snapshot rather than a second transient compile pipeline

## Implementation Note: Richer Child Scheduling And Blocker Explanation

- `node child-materialization --node <id>` now returns richer per-child scheduling detail:
  - `scheduling_status`
  - `scheduling_reason`
  - blocker payloads
- `node blockers --node <id>` now reflects both dependency-derived and runtime-derived blockers such as pause gates, missing compiled workflows, already-running nodes, and non-ready lifecycle states
- `tree show --node <id> --full` now includes summarized scheduling visibility on each row through `scheduling_status` and `blocker_count`
