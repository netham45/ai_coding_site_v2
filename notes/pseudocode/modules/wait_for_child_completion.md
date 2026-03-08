# Module: `wait_for_child_completion(...)`

## Purpose

Represent the parent-side waiting behavior after child materialization and scheduling, including the transition from ordinary waiting to impossible-wait detection, child-failure ingestion, or parent reconciliation readiness.

---

## Source notes

Primary:

- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`

Supporting:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

---

## Inputs

- `parent_node_version_id`
- active child set
- current child scheduling classifications
- parent policy for required children

---

## Required state

- child materialization has already occurred
- authoritative child statuses are queryable
- parent can determine which children are required for the current parent stage

---

## Outputs

- `WaitResult(status = "waiting" | "ready_to_reconcile" | "child_failed" | "paused_for_user")`

Optional outputs:

- blocking child IDs
- failed child IDs
- parent reconciliation summary

---

## Durable writes

- parent waiting-state transition if needed
- waiting snapshot including blockers
- child-failure ingestion event where applicable
- parent reconciliation-ready event where applicable

---

## Decision algorithm

```text
function wait_for_child_completion(parent_node_version_id):
  required_children = load_required_children_for_current_parent_stage(parent_node_version_id)
  child_states = load_authoritative_child_states(parent_node_version_id)

  if any(required_child_is_failed(child_states, child_id) for child_id in required_children):
    failed_children = list_failed_required_children(child_states, required_children)
    ingest_child_failures_into_parent_context(parent_node_version_id, failed_children)
    return WaitResult(status = "child_failed", failed_children = failed_children)

  if any(required_child_is_in_impossible_wait(child_states, child_id) for child_id in required_children):
    record_parent_pause_reason(parent_node_version_id, "required_child_impossible_wait")
    return WaitResult(status = "paused_for_user")

  if all(required_child_is_complete(child_states, child_id) for child_id in required_children):
    record_parent_reconciliation_ready(parent_node_version_id, required_children)
    return WaitResult(status = "ready_to_reconcile")

  blockers = list_incomplete_required_children(child_states, required_children)
  mark_parent_waiting_on_children(parent_node_version_id, blockers)
  return WaitResult(status = "waiting", blocking_children = blockers)
```

---

## Waiting rules

- default parent behavior assumes all materialized children for the active layout are required unless narrower scope is declared
- waiting is valid only while the blocker set is still resolvable
- waiting must not mask failed children or impossible waits

---

## Failure and escalation behavior

- when a required child fails, this module should not decide the final parent response
- it should ingest the failure durably and hand control to parent failure decision logic
- when blockers can never resolve, the parent should not wait indefinitely

---

## Pause/recovery behavior

- waiting state must survive restart and recovery
- recomputing waiting after restart should reproduce the same blocker set from durable child state

---

## CLI-visible expectations

Operators should be able to inspect:

- whether the parent is waiting on children
- which required children are blocking progress
- whether the wait is ordinary or impossible
- whether reconciliation is now allowed

---

## Open questions

- whether impossible-wait should immediately invoke parent failure decision logic rather than pause first
- whether partially optional child sets need a distinct required-child selector artifact

---

## Pseudotests

### `waits_when_required_children_are_incomplete_but_resolvable`

Given:

- at least one required child is incomplete
- no required child is failed

Expect:

- parent is marked waiting on children

### `returns_ready_to_reconcile_when_all_required_children_complete`

Given:

- all required children are `COMPLETE`

Expect:

- parent becomes ready to reconcile

### `ingests_child_failure_instead_of_waiting_forever`

Given:

- a required child has failed

Expect:

- parent receives child-failure input
- ordinary waiting does not continue
