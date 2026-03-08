# Module: `execute_compiled_subtask(...)`

## Purpose

Dispatch one compiled subtask to the correct handler and normalize its result into one of three loop-level outcomes:

- `ok`
- `pause`
- `failed`

This module is the execution boundary between the generic node loop and subtask-type-specific behavior.

---

## Source notes

Primary:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`

Supporting:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`

---

## Inputs

- `run_id`
- `compiled_subtask`
- `attempt_id`
- `session_id`
- current run context
- current task/subtask context from the compiled workflow

---

## Required state

- compiled subtask exists in the authoritative compiled workflow for the run
- all dependency prerequisites for the subtask are satisfied or the subtask type explicitly represents waiting
- prompt/command/context retrieval surfaces are available through CLI
- the session is bound to the run or is a bounded child session delegated by the parent session

---

## Outputs

- normalized `SubtaskResult`
- optional output artifacts
- optional summary path
- optional pause flag
- optional failure classification
- optional returned child-session payload

---

## Durable writes

- subtask-attempt input snapshot
- handler-specific artifacts or summaries
- child-session records where applicable
- validation/review/testing/docs/provenance results where applicable
- changed-file and git-head snapshots where applicable

---

## Dispatcher

```text
function execute_compiled_subtask(run_id, compiled_subtask, attempt_id, session_id):
  assert compiled_subtask_belongs_to_run(run_id, compiled_subtask.id)
  input_snapshot = build_subtask_input_snapshot(run_id, compiled_subtask.id)
  persist_subtask_attempt_input_snapshot(attempt_id, input_snapshot)

  handler = select_handler_for_subtask_type(compiled_subtask.type)

  raw_result = handler(
    run_id = run_id,
    compiled_subtask = compiled_subtask,
    attempt_id = attempt_id,
    session_id = session_id,
    input_snapshot = input_snapshot
  )

  normalized_result = normalize_handler_result(raw_result, compiled_subtask.type)
  assert normalized_result.status in ["ok", "pause", "failed"]
  return normalized_result
```

---

## Handler families

Expected first-pass handler families:

- `run_prompt`
- `run_command`
- `build_context`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `validate`
- `review`
- `run_tests`
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`
- `spawn_child_node`
- `reset_to_seed`
- `merge_children`
- `update_provenance`

---

## Handler rules

### Prompt and command handlers

- retrieve prompt/command/context through CLI-visible surfaces
- preserve enough input and output detail for later inspection
- return `failed` rather than silently swallow execution errors

### Waiting handlers

- if prerequisites are not met but waiting is valid, return `pause` or a bounded waiting result according to policy
- do not fabricate success without the required dependency state

### Validation/review/testing handlers

- persist results in typed durable records
- return `failed` when required gates reject progression
- return `pause` if policy requires user decision after the result

### Child session handler

- push bounded child session
- persist merge-back contract
- parent subtask remains cursor owner
- returned result must be validated before parent progression continues

### Child node handler

- materialize or schedule child nodes durably
- do not claim success until the child orchestration contract for this subtask is satisfied

---

## Failure paths

### Unsupported subtask type

- fail immediately
- classify as runtime structure failure or unknown handler type

### Dependency precondition violation

- fail if the subtask is not a waiting-type subtask and required dependencies are missing
- do not let execution guess around bad compile output

### Child session return contract invalid

- classify as failure
- preserve child session ID and merge-back validation reason

### Environment setup failure

- classify according to environment/runtime policy
- preserve requested isolation mode if relevant

---

## Pause/recovery behavior

- a handler may return `pause` only with an explicit pause reason or flag
- a handler must not advance the run cursor itself
- interrupted handler execution should be recoverable from durable attempt state, input snapshot, and current cursor

---

## CLI-visible expectations

The session should be able to retrieve:

- current prompt
- current command
- current context
- prior summaries and child summaries when relevant
- instructions for completion, failure, or child-session merge-back

---

## Open questions

- whether waiting handlers should map to pause states or distinct waiting run states at the loop boundary
- how much handler-specific output should be normalized versus left typed in module-specific result tables
- whether `finalize_node` remains a handler or should become a loop-owned terminal phase only

---

## Pseudotests

### `dispatches_by_compiled_subtask_type`

Given:

- a compiled subtask of type `run_prompt`

Expect:

- the prompt handler is selected
- the normalized result shape is returned

### `preserves_input_snapshot_before_execution`

Given:

- a runnable compiled subtask

Expect:

- attempt input snapshot is written before handler work begins

### `rejects_invalid_child_session_return_payload`

Given:

- a `spawn_child_session` handler returns malformed merge-back data

Expect:

- result is normalized to `failed`
- diagnostics preserve the child session context
