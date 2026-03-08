# Orchestration And State Pseudotests

## Purpose

These pseudotests cover the orchestration-edge modules and state machines that are not fully covered by the runtime-core or rectification/cutover suites.

Covered artifacts:

- `materialize_layout_children(...)`
- `schedule_ready_children(...)`
- `wait_for_child_completion(...)`
- `collect_child_results(...)`
- `handle_child_failure_at_parent(...)`
- `state_machines/node_lifecycle.md`
- `state_machines/parent_child_authority.md`

Use [TEST_FORMAT.md](/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2/notes/pseudocode/pseudotests/TEST_FORMAT.md) as the review standard.

---

## Child materialization

### `layout_authoritative_parent_materializes_valid_child_set`

Scenario:

- a layout-authoritative parent receives a valid authoritative layout

Applies to:

- `modules/materialize_layout_children.md`
- `state_machines/parent_child_authority.md`

Preconditions:

- parent authority mode is `layout_authoritative`
- layout IDs are unique
- dependency graph is valid

Action:

- run `materialize_layout_children(parent_node_version_id, layout)`

Expected durable effects:

- child node versions are created
- parent-child edges are persisted
- child dependency edges are persisted
- child origin is recorded as `layout_generated`

Expected forbidden effects:

- no partial materialization becomes authoritative after validation failure

Expected operator-visible results:

- created children and dependency edges are queryable

Pass rule:

- pass only if creation, edge persistence, and fail-fast behavior are all explicit

### `hybrid_parent_blocks_silent_structural_replacement`

Scenario:

- a hybrid parent receives a new layout

Applies to:

- `modules/materialize_layout_children.md`
- `state_machines/parent_child_authority.md`

Preconditions:

- authority mode is `hybrid`

Action:

- run `materialize_layout_children(...)`

Expected durable effects:

- reconciliation-required or equivalent control result is recorded

Expected forbidden effects:

- child set must not be silently replaced

Expected operator-visible results:

- reconciliation requirement is visible

Pass rule:

- pass only if the module explicitly blocks structural mutation in hybrid mode

### `invalid_layout_cycle_fails_before_child_creation`

Scenario:

- child layout contains a dependency cycle

Applies to:

- `modules/materialize_layout_children.md`

Preconditions:

- cycle is detectable from layout definitions

Action:

- run materialization

Expected durable effects:

- validation failure is recorded

Expected forbidden effects:

- no child node versions are created

Expected operator-visible results:

- cycle failure is inspectable

Pass rule:

- pass only if cycle validation happens before structural persistence

---

## Scheduling

### `ready_child_is_not_blocked_by_unrelated_incomplete_sibling`

Scenario:

- child A is runnable
- child B is incomplete but not a dependency

Applies to:

- `modules/schedule_ready_children.md`

Preconditions:

- dependency edges do not require B for A

Action:

- run `schedule_ready_children(parent_node_version_id)`

Expected durable effects:

- child A is classified `ready`

Expected forbidden effects:

- A must not be blocked by generic sibling incompleteness

Expected operator-visible results:

- readiness explanation shows only actual blockers

Pass rule:

- pass only if readiness depends on explicit edges rather than blanket sibling completion

### `already_running_child_is_not_restarted`

Scenario:

- a child is already running

Applies to:

- `modules/schedule_ready_children.md`

Preconditions:

- authoritative child state shows active execution

Action:

- run scheduling again

Expected durable effects:

- child is classified `already_running`

Expected forbidden effects:

- no duplicate child start/admission occurs

Expected operator-visible results:

- classification explains why no new start happened

Pass rule:

- pass only if rerun safety is explicit

### `impossible_wait_is_not_treated_as_normal_block`

Scenario:

- child depends on another child that failed with no viable recovery path

Applies to:

- `modules/schedule_ready_children.md`
- `modules/wait_for_child_completion.md`

Preconditions:

- dependency target cannot satisfy required state under current lineage

Action:

- run scheduling and then waiting evaluation

Expected durable effects:

- impossible-wait condition is recorded or surfaced

Expected forbidden effects:

- parent must not wait indefinitely as if the blocker were ordinary

Expected operator-visible results:

- blocker is described as impossible, not merely pending

Pass rule:

- pass only if the artifacts distinguish resolvable waiting from impossible waiting

---

## Parent waiting and child result collection

### `parent_reaches_reconcile_ready_only_when_required_children_complete`

Scenario:

- all required children are complete
- optional or unrelated children may still exist

Applies to:

- `modules/wait_for_child_completion.md`
- `modules/collect_child_results.md`

Preconditions:

- required-child selector is known

Action:

- collect child results and evaluate waiting state

Expected durable effects:

- parent reconciliation-ready event or equivalent is recorded

Expected forbidden effects:

- parent must not reconcile before required children are complete

Expected operator-visible results:

- required completion basis is inspectable

Pass rule:

- pass only if readiness is tied to required children, not vague overall progress

### `child_result_collection_uses_authoritative_version_only`

Scenario:

- a child has both candidate and authoritative versions

Applies to:

- `modules/collect_child_results.md`
- `state_machines/lineage_authority.md`

Preconditions:

- candidate is newer but not cut over

Action:

- run `collect_child_results(parent_node_version_id)`

Expected durable effects:

- authoritative child result is selected

Expected forbidden effects:

- candidate child must not replace authoritative input

Expected operator-visible results:

- authoritative selection basis is queryable

Pass rule:

- pass only if authority selection is explicit and non-guessing

---

## Parent failure decisions

### `parent_retries_child_for_retryable_transient_failure`

Scenario:

- child failure is transient
- budget remains

Applies to:

- `modules/handle_child_failure_at_parent.md`

Preconditions:

- counters are below threshold

Action:

- run parent child-failure handling

Expected durable effects:

- counter updates are persisted
- retry decision is recorded

Expected forbidden effects:

- parent must not immediately pause or replan without policy justification

Expected operator-visible results:

- decision history explains retry choice

Pass rule:

- pass only if retry decision order and counter use are explicit

### `parent_replans_when_child_failure_indicates_bad_layout_or_requirements`

Scenario:

- child failure class indicates bad layout or bad requirements

Applies to:

- `modules/handle_child_failure_at_parent.md`
- `state_machines/parent_child_authority.md`

Preconditions:

- parent policy allows replanning

Action:

- handle child failure at parent

Expected durable effects:

- replan summary is registered
- parent enters replanning path

Expected forbidden effects:

- system must not keep retrying a structurally bad child plan indefinitely

Expected operator-visible results:

- parent summary explains why replan was chosen

Pass rule:

- pass only if structural-failure classes can trigger replan explicitly

### `parent_pauses_when_failure_thresholds_are_exceeded`

Scenario:

- total, consecutive, or per-child thresholds are exceeded

Applies to:

- `modules/handle_child_failure_at_parent.md`
- `state_machines/node_lifecycle.md`

Preconditions:

- counters exceed policy thresholds

Action:

- handle child failure

Expected durable effects:

- parent summary is registered
- parent transitions to paused state

Expected forbidden effects:

- parent must not continue autonomous retries after threshold exhaustion

Expected operator-visible results:

- threshold-based deferment is visible

Pass rule:

- pass only if threshold logic clearly overrides autonomous continuation

---

## Lifecycle state machine

### `compile_failed_node_cannot_be_admitted_or_run`

Scenario:

- node lifecycle state is `COMPILE_FAILED`

Applies to:

- `state_machines/node_lifecycle.md`
- `modules/compile_workflow.md`

Preconditions:

- latest compile attempt failed

Action:

- evaluate admission and execution eligibility

Expected durable effects:

- none beyond the existing blocked state

Expected forbidden effects:

- no run admission
- no transition to `RUNNING`

Expected operator-visible results:

- compile failure remains the blocking explanation

Pass rule:

- pass only if both the state machine and compile module block admission

### `paused_for_user_does_not_resume_implicitly`

Scenario:

- node is paused for user

Applies to:

- `state_machines/node_lifecycle.md`
- `modules/run_node_loop.md`

Preconditions:

- pause flag is unresolved

Action:

- attempt normal progression

Expected durable effects:

- paused state remains

Expected forbidden effects:

- no automatic transition back to `RUNNING`

Expected operator-visible results:

- pause reason remains visible

Pass rule:

- pass only if resume requires explicit gate clearing

### `superseded_node_cannot_return_to_active_execution`

Scenario:

- node version is superseded

Applies to:

- `state_machines/node_lifecycle.md`
- `state_machines/lineage_authority.md`

Preconditions:

- newer authoritative version exists

Action:

- evaluate whether old version can be admitted again

Expected durable effects:

- none beyond preserved history

Expected forbidden effects:

- superseded version must not restart as current active lineage

Expected operator-visible results:

- historical status remains queryable without being current

Pass rule:

- pass only if supersession is terminal for ordinary execution
