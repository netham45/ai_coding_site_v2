# Module: `run_node_loop(...)`

## Purpose

Run the authoritative execution loop for one admitted node run.

This module owns cursor progression through compiled subtasks, runtime-visible stage transitions, and the handoff between subtask execution, pause behavior, failure handling, and finalization.

---

## Source notes

Primary:

- `notes/runtime_command_loop_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_pseudocode_plan.md`

Supporting:

- `notes/cli_surface_spec_v2.md`
- `notes/state_value_catalog.md`
- `notes/pause_workflow_event_persistence.md`
- `notes/parent_failure_decision_spec.md`

---

## Inputs

- `node_id`
- active `node_run_id` or instruction to admit/load one
- active compiled workflow binding
- current execution cursor
- active primary session binding or recovery path

---

## Required state

- node version is compiled and runnable
- there is at most one authoritative active run for the node version
- the current compiled workflow snapshot is durable and queryable
- the current cursor is durable and queryable
- the primary session binding is unique or recoverable

---

## Outputs

On loop continuation:

- current subtask attempt history updated
- outputs, summaries, validations, and cursor state updated

On pause:

- pause summary and pause flag persisted
- run transitions to paused state without cursor corruption

On failure:

- failure summary persisted
- failure handler invoked
- retry, pause, or fail-to-parent decision persisted

On completion:

- finalization runs
- node reaches its next canonical post-run lifecycle state

---

## Durable writes

- active run load or admission record
- session binding or session recovery record
- current subtask attempt creation and status transitions
- heartbeat and progress records
- subtask outputs and summaries
- validation/review/testing/docs/provenance result records where applicable
- cursor advancement records
- pause or failure events where applicable
- finalization result where applicable

---

## Happy path

```text
function run_node_loop(node_id):
  run = admit_or_load_active_run(node_id)
  assert run is not null

  session = bind_or_resume_primary_session(run.id)
  assert session is not null

  while true:
    run_state = load_authoritative_run_state(run.id)
    assert run_state_matches_compiled_workflow(run_state)

    if run_state.lifecycle_state in ["PAUSED_FOR_USER", "FAILED_TO_PARENT", "COMPLETE", "CANCELLED"]:
      return LoopResult(status = "stopped", state = run_state.lifecycle_state)

    subtask = get_current_compiled_subtask(run.id)

    if subtask is null:
      finalize_completed_workflow(run.id, session.id)
      return LoopResult(status = "completed")

    attempt = create_or_resume_subtask_attempt(
      run_id = run.id,
      compiled_subtask_id = subtask.id,
      session_id = session.id
    )

    mark_subtask_started(run.id, subtask.id, attempt.id, session.id)
    record_session_heartbeat(session.id, subtask.id)

    result = execute_compiled_subtask(
      run_id = run.id,
      compiled_subtask = subtask,
      attempt_id = attempt.id,
      session_id = session.id
    )

    if result.status == "ok":
      persist_subtask_outputs(run.id, subtask.id, attempt.id, result)
      run_required_acceptance_checks(run.id, subtask.id, attempt.id, result)
      mark_subtask_complete(run.id, subtask.id, attempt.id)
      advance_cursor(run.id, from_subtask_id = subtask.id)
      continue

    if result.status == "pause":
      persist_subtask_outputs_if_any(run.id, subtask.id, attempt.id, result)
      register_summary(node_id, result.summary_path, "pause")
      mark_subtask_paused(run.id, subtask.id, attempt.id, result.pause_flag_name)
      transition_run_to_paused(run.id, result.pause_flag_name)
      record_pause_event(run.id, subtask.id, result.pause_flag_name)
      return LoopResult(status = "paused", pause_flag_name = result.pause_flag_name)

    if result.status == "failed":
      persist_subtask_outputs_if_any(run.id, subtask.id, attempt.id, result)
      register_summary(node_id, result.summary_path, "failure")
      mark_subtask_failed(run.id, subtask.id, attempt.id, result.failure_class)
      decision = handle_subtask_failure(
        run_id = run.id,
        compiled_subtask_id = subtask.id,
        attempt_id = attempt.id,
        failure_result = result
      )
      if decision.status in ["retry_scheduled", "recovered_in_place"]:
        continue
      return LoopResult(status = decision.status)

    raise RuntimeInvariantError("Unknown subtask result status")
```

---

## Loop invariants

- the cursor advances only after accepted successful completion
- pause and failure do not implicitly advance the cursor
- the parent session remains the owner of cursor progression even if a child session is pushed temporarily
- the compiled workflow does not change during a run unless the run is explicitly aborted and superseded

---

## Failure paths

### Session binding failure

- do not start execution if a unique authoritative session cannot be established
- invoke recovery or pause for operator intervention

### Cursor mismatch

- if current cursor points to a missing or superseded compiled subtask, stop execution
- record invariant failure
- require recovery or operator intervention

### Post-subtask acceptance failure

- if outputs exist but required validations reject them, treat as subtask failure
- do not advance the cursor

### Duplicate active session ambiguity

- stop automatic execution
- mark an ambiguity event
- require explicit recovery or operator resolution

---

## Pause/recovery behavior

- if the run is already paused when the loop loads state, return without attempting execution
- if a subtask returns `pause`, the loop persists the pause state and exits cleanly
- if the session is lost mid-loop, recovery logic must restore the same cursor and compiled workflow before execution resumes

---

## CLI-visible expectations

The following information must be queryable while this loop runs:

- current run state
- current compiled subtask
- current attempt number and status
- latest subtask summary
- pause reason if paused
- failure summary and decision if failed

---

## Open questions

- should the loop itself perform nudge decisions or only delegate to a supervisor/recovery path
- which lifecycle transitions belong on `node_versions` versus `node_runs` for intermediate quality-gate stages
- whether finalization should be a normal compiled subtask everywhere or a loop-owned terminal helper

---

## Pseudotests

### `advances_only_after_accepted_completion`

Given:

- subtask handler returns success
- required validations pass

Expect:

- attempt is completed
- cursor advances exactly once

### `does_not_advance_on_pause`

Given:

- subtask returns `pause`

Expect:

- run becomes paused
- current compiled subtask remains the same on resume

### `does_not_advance_on_failure`

Given:

- subtask returns `failed`

Expect:

- failure handler runs
- cursor remains on the failing subtask unless a retry/reset policy explicitly rewrites it
