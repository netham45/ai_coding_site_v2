# Module: `handle_child_failure_at_parent(...)`

## Purpose

Take a child failure that has already escalated to the parent and choose the parent's next durable response:

- retry child
- regenerate child
- replan parent
- pause for user

This module is the parent-side analogue of `handle_subtask_failure(...)`.

---

## Source notes

Primary:

- `notes/parent_failure_decision_spec.md`
- `notes/runtime_command_loop_spec_v2.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `parent_node_version_id`
- `failed_child_node_version_id`
- latest child failure summary
- parent failure counters
- parent failure and replanning policy
- sibling-child completion state

---

## Required state

- child failure has already been durably recorded
- parent-child relationship is authoritative and queryable
- parent counters and prior decision history are queryable

---

## Outputs

- `ParentFailureDecision(status = "retry_child" | "regenerate_child" | "replan_parent" | "paused_for_user")`

Optional outputs:

- decision summary
- affected child set
- parent replan trigger

---

## Durable writes

- parent failure counters
- parent decision event/history
- parent summary when pausing or replanning
- child retry or regeneration schedule event where applicable

---

## Decision algorithm

```text
function handle_child_failure_at_parent(parent_node_version_id, failed_child_node_version_id):
  failure = load_latest_child_failure(failed_child_node_version_id)
  policy = load_parent_failure_policy(parent_node_version_id)
  counters = increment_parent_failure_counters(parent_node_version_id, failed_child_node_version_id)
  classification = classify_child_failure(failure)

  record_failure_against_parent(parent_node_version_id, failed_child_node_version_id, failure, classification)

  if thresholds_exceeded(counters, policy):
    summary = build_parent_pause_summary(parent_node_version_id, failed_child_node_version_id, failure, counters)
    register_summary(parent_node_version_id, summary, "parent_child_failure_pause")
    record_parent_decision(parent_node_version_id, failed_child_node_version_id, "pause_for_user", classification)
    transition_parent_to_paused(parent_node_version_id)
    return ParentFailureDecision(status = "paused_for_user")

  if should_retry_child(classification, failed_child_node_version_id, policy):
    schedule_child_retry(failed_child_node_version_id)
    record_parent_decision(parent_node_version_id, failed_child_node_version_id, "retry_child", classification)
    return ParentFailureDecision(status = "retry_child")

  if should_regenerate_child(classification, failed_child_node_version_id, policy):
    schedule_child_regeneration(failed_child_node_version_id)
    record_parent_decision(parent_node_version_id, failed_child_node_version_id, "regenerate_child", classification)
    return ParentFailureDecision(status = "regenerate_child")

  if should_replan_parent(parent_node_version_id, failed_child_node_version_id, classification, policy):
    summary = build_parent_replan_summary(parent_node_version_id, failed_child_node_version_id, failure, counters)
    register_summary(parent_node_version_id, summary, "parent_replan")
    record_parent_decision(parent_node_version_id, failed_child_node_version_id, "replan_parent", classification)
    enter_parent_replan_flow(parent_node_version_id)
    return ParentFailureDecision(status = "replan_parent")

  summary = build_parent_pause_summary(parent_node_version_id, failed_child_node_version_id, failure, counters)
  register_summary(parent_node_version_id, summary, "parent_child_failure_pause")
  record_parent_decision(parent_node_version_id, failed_child_node_version_id, "pause_for_user", classification)
  transition_parent_to_paused(parent_node_version_id)
  return ParentFailureDecision(status = "paused_for_user")
```

---

## Counter semantics

Track at least:

- total child failure count
- consecutive child failure count
- per-child failure count

Use them differently:

- consecutive failures indicate immediate stuckness
- total failures indicate broader instability
- per-child failures indicate localized regeneration or replanning need

---

## Parent summary requirements

When the parent pauses or replans, summary data should include:

- failed child IDs
- failure classes
- failed stages or subtasks
- retries already attempted
- whether sibling children succeeded
- likely root cause
- chosen action and why

---

## Failure paths

### Unknown failure classification

- preserve uncertainty explicitly
- bias toward pause or replan rather than destructive guessing

### Parent already degraded or paused

- avoid stacking contradictory decisions
- append to existing parent decision history

### Child authority ambiguity after failure

- if the failed child version is no longer authoritative and replacement lineage is unclear, pause for user

---

## Pause/recovery behavior

- parent pause preserves current child-failure context
- regeneration or retry should target the correct authoritative or explicitly selected child version
- unaffected healthy siblings should remain reusable if policy allows

---

## CLI-visible expectations

Operators should be able to inspect:

- parent child-failure counters
- decision history
- why the parent chose retry, regeneration, replan, or pause

---

## Open questions

- whether parent-local replan should automatically identify reusable healthy siblings or require a separate reconciliation planning module
- how parent decision policy should vary between normal generation and rectification flows

---

## Pseudotests

### `retries_child_when_failure_is_retryable_and_budget_remains`

Given:

- child failure is transient
- budget remains

Expect:

- parent schedules retry

### `replans_parent_when_failure_indicates_bad_layout`

Given:

- child failure indicates bad layout or bad requirements

Expect:

- parent enters replanning path

### `pauses_when_thresholds_are_exceeded`

Given:

- failure counters exceed parent policy thresholds

Expect:

- parent pauses for user
- structured parent summary is registered
