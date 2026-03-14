# Unified Command Lifecycle Contract

## Purpose

Capture the workflow-overhaul direction for replacing ad hoc YAML-command lifecycle behavior with one daemon-owned lifecycle contract shared across executable command kinds and adjacent action surfaces.

This is a future-plan note.

It is not an implementation claim.

## Problem Statement

The current command semantics are split across multiple surfaces:

- task and subtask YAML definitions
- compile-time subtask shaping
- daemon execution and mutation paths
- CLI mutation and inspection surfaces
- intervention/recommended-action surfaces
- review/testing/docs result-routing policies

The result is that command truth is harder to reason about than it should be:

- blocked/completed/failed behavior is not represented by one canonical interface
- legality and allowed-action behavior are split across command kinds
- some command-like surfaces are modeled as task/subtask execution while others are modeled as interventions or runtime actions
- YAML can imply lifecycle behavior without one obvious code-owned contract

## Core Recommendation

Do not model command lifecycle with callback-heavy command objects such as:

- `begin(fail_callback, end_callback, complete_callback)`
- `is_blocked()`
- `is_complete()`

Instead, standardize on a daemon-owned lifecycle contract with structured legality and structured action results.

Recommended conceptual interface:

```python
class CommandHandler:
    def describe(self) -> dict[str, object]: ...
    def get_status(self, ctx) -> CommandSnapshot: ...
    def get_allowed_actions(self, ctx) -> list[str]: ...
    def can_begin(self, ctx, params) -> LegalityResult: ...
    def begin(self, ctx, params) -> CommandActionResult: ...
    def can_complete(self, ctx, result) -> LegalityResult: ...
    def complete(self, ctx, result) -> CommandActionResult: ...
    def fail(self, ctx, error) -> CommandActionResult: ...
```

Recommended command state vocabulary:

- `pending`
- `ready`
- `running`
- `blocked`
- `completed`
- `failed`
- `cancelled`

Recommended legality/result model:

- legality should return structured `allowed/code/summary/details`
- action execution should return structured `accepted/state/code/summary/next_actions/payload`

## Required Foundation Layer

The per-command migration plans are not sufficient by themselves.

This command family also needs explicit foundation planning for:

- the shared abstract lifecycle interface every command kind must implement or adapt into
- the shared command state, legality, and action-result models
- the registry and runtime dispatch path that resolves compiled command kinds to handlers
- the YAML-to-operator projection contract that keeps CLI and website surfaces daemon-owned and consistent

The command-specific plans should depend on those shared foundation plans rather than each command redefining the same abstractions in parallel.

## YAML Boundary

YAML should remain declarative.

YAML may declare:

- command kind
- required inputs
- retry policy
- completion checks
- failure routing

YAML should not own:

- live legality checks
- blocked-reason computation
- durable transition truth
- runtime mutation authorization

## Full In-Scope Inventory

If this contract is adopted, it should be a full-system migration rather than a partial first pass.

### A. Built-in executable subtask command kinds

- `run_prompt`
- `run_command`
- `run_tests`
- `validate`
- `review`
- `build_context`
- `build_docs`
- `write_summary`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `spawn_child_node`
- `spawn_child_session`
- `merge_children`
- `update_provenance`
- `finalize_node`
- `reset_to_seed`
- `recover_cursor`
- `rebind_session`
- `pause_on_user_flag`
- `record_merge_metadata`
- `collect_child_summaries`
- `finalize_git_state`
- `nudge_session`

### B. Built-in task definitions that compose those commands

- `build_node_docs`
- `execute_node`
- `finalize_node`
- `generate_child_layout`
- `nudge_idle_session`
- `pause_for_user`
- `reconcile_children`
- `reconcile_merge_conflict`
- `recover_interrupted_run`
- `rectify_node_from_seed`
- `rectify_upstream`
- `research_context`
- `respond_to_child_failure`
- `review_child_layout`
- `review_node`
- `revise_child_layout`
- `spawn_children`
- `summarize_failure`
- `test_node`
- `update_provenance`
- `validate_node`
- `wait_for_children`
- `wait_for_dependencies`

### C. Runtime and intervention action surfaces

- `approve_pause`
- `abort_merge`
- `resolve_conflict`
- `resume_session`
- child reconciliation decisions exposed by the intervention catalog

### D. Runtime policy action refs

- `rebind_session`
- `recover_cursor`
- `spawn_child_session`
- `nudge_session`
- `write_summary`

### E. Failure and result routing actions that must align with the same model

- `fail_to_parent`
- `pause_for_user`
- `continue`
- `rerun_task`
- `rerun_subtask`
- `allow_override`

## Recommended Examples

### Example: `run_command`

Expected lifecycle posture:

- begin only when the compiled subtask is runnable
- record structured command execution result
- complete only when required checks pass
- fail with structured exit/error payload when checks fail

### Example: `wait_for_children`

Expected lifecycle posture:

- begin when child materialization is already authoritative
- remain `blocked` with a concrete reason while required children remain incomplete
- complete only when all required children satisfy the readiness predicate
- surface structured blocked reasons and remaining children through CLI and website inspection

## Migration Rule

If a surface can be:

- declared in YAML as executable behavior
- started, completed, blocked, failed, retried, or resumed
- exposed in CLI or website surfaces as an allowed action or recommended action
- applied by the daemon as a bounded mutation

then it belongs under the unified command/action lifecycle model.

## Placement In The Workflow Overhaul

This should be planned as part of the workflow overhaul, not as a separate later cleanup pass.

Recommended placement:

- after workflow-profile and templated-task-generation structure is frozen enough to avoid designing around obsolete assumptions
- before final route/mutation/UI/E2E rollout so the overhaul does not land on top of split command semantics
