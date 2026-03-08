# Module: `handle_subtask_failure(...)`

## Purpose

Take a failed compiled subtask result and choose the next durable control action:

- retry current subtask
- pause for user
- fail node to parent
- trigger a parent-visible replanning path where policy allows

This module makes retry and escalation behavior deterministic rather than session-improvised.

---

## Source notes

Primary:

- `notes/runtime_command_loop_spec_v2.md`
- `notes/parent_failure_decision_spec.md`
- `notes/node_lifecycle_spec_v2.md`

Supporting:

- `notes/runtime_pseudocode_plan.md`
- `notes/state_value_catalog.md`
- `notes/cli_surface_spec_v2.md`

---

## Inputs

- `run_id`
- `compiled_subtask_id`
- `attempt_id`
- `failure_result`
- compiled retry policy for the subtask
- current run failure counters
- current parent relationship if the node has a parent

---

## Required state

- failure summary is already persisted before decision logic runs
- retry policy is durable and queryable
- the current attempt is terminally marked failed before control decisions are made

---

## Outputs

- `FailureDecision(status = "retry_scheduled" | "paused_for_user" | "failed_to_parent" | "recovered_in_place")`

Optional outputs:

- retry scheduling metadata
- pause flag and summary
- parent escalation event

---

## Durable writes

- failure classification for the attempt
- updated retry and failure counters
- decision record describing chosen action and rationale
- pause event or parent-escalation event where applicable

---

## Decision algorithm

```text
function handle_subtask_failure(run_id, compiled_subtask_id, attempt_id, failure_result):
  run_state = load_authoritative_run_state(run_id)
  policy = load_subtask_retry_policy(compiled_subtask_id)
  classification = classify_failure(failure_result)

  increment_failure_counters(run_id, compiled_subtask_id, classification)

  if exceeds_hard_stop_thresholds(run_state, policy, classification):
    summary = build_pause_summary_for_failure(run_id, compiled_subtask_id, classification)
    record_failure_decision(run_id, compiled_subtask_id, "paused_for_user", classification, summary)
    transition_run_to_paused(run_id, pause_flag_name = "failure_threshold_exceeded")
    return FailureDecision(status = "paused_for_user")

  if failure_is_retryable(classification, policy) and retry_budget_remains(run_id, compiled_subtask_id, policy):
    schedule_retry_of_current_subtask(run_id, compiled_subtask_id)
    record_failure_decision(run_id, compiled_subtask_id, "retry_scheduled", classification)
    return FailureDecision(status = "retry_scheduled")

  if failure_requires_user_gate(classification, policy):
    summary = build_pause_summary_for_failure(run_id, compiled_subtask_id, classification)
    record_failure_decision(run_id, compiled_subtask_id, "paused_for_user", classification, summary)
    transition_run_to_paused(run_id, pause_flag_name = "subtask_failure_requires_user")
    return FailureDecision(status = "paused_for_user")

  fail_node_to_parent(run_id, compiled_subtask_id, classification, failure_result.summary_path)
  record_failure_decision(run_id, compiled_subtask_id, "failed_to_parent", classification)
  return FailureDecision(status = "failed_to_parent")
```

---

## Failure classification expectations

The classifier should distinguish at least:

- transient execution failure
- validation failure
- review failure
- test failure
- dependency or context failure
- merge conflict unresolved
- environment failure
- unknown failure

These categories drive retryability and escalation.

---

## Parent interaction

If the node has a parent and failure escalates:

- the child does not directly fail the whole tree
- the child records `FAILED_TO_PARENT` or equivalent durable failed state
- the parent becomes the next decision-maker
- the escalation payload must preserve child failure summary, failing stage, retry history, and dependency impact

---

## Pause/recovery behavior

- retries must resume from the same compiled subtask unless policy explicitly resets more state
- pause must preserve the current cursor and failure context
- recovery after interruption must not erase failure counters or decision history

---

## CLI-visible expectations

It must be possible to inspect:

- the latest failure class
- retry budget consumed and remaining
- the final decision taken
- whether the node is paused or failed to parent

---

## Open questions

- whether some parent-local replanning decisions should originate here or only after the parent ingests the child failure
- whether retry budgets should be counted per run, per subtask, or both

---

## Pseudotests

### `retries_retryable_failure_when_budget_remains`

Given:

- failure is transient
- retry budget remains

Expect:

- retry is scheduled
- cursor remains on the same compiled subtask

### `pauses_when_failure_threshold_exceeded`

Given:

- repeated failures exceed policy thresholds

Expect:

- run becomes paused for user
- decision history records threshold exhaustion

### `fails_to_parent_when_not_retryable_and_no_user_pause_applies`

Given:

- failure is not retryable
- no policy requires pause first

Expect:

- node transitions to failed-to-parent
- escalation payload is queryable
