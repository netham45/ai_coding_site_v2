# Module: `admit_node_run(...)`

## Purpose

Determine whether a node version is eligible to start execution and, if eligible, create the authoritative node run and initialize its cursor.

---

## Source notes

Primary:

- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_pseudocode_plan.md`

Supporting:

- `notes/runtime_command_loop_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/state_value_catalog.md`
- `notes/pause_workflow_event_persistence.md`

---

## Inputs

- `node_id` or `node_version_id`
- current lifecycle state
- compiled workflow binding
- dependency-readiness result
- active run state if any
- current pause flag state

---

## Required state

- authoritative node version is resolvable
- compiled workflow exists for runnable nodes
- dependency readiness can be checked deterministically
- active run uniqueness can be checked

---

## Outputs

- `AdmissionResult(status = "admitted" | "blocked" | "rejected")`

Optional outputs:

- `node_run_id`
- blocker reason
- current conflicting run ID

---

## Durable writes

- `node_runs` row on successful admission
- initial cursor state
- admission decision event or blocker summary where applicable

---

## Decision algorithm

```text
function admit_node_run(node_id):
  node = load_authoritative_node_version(node_id)
  lifecycle = load_node_lifecycle_state(node.id)
  compiled_workflow = load_compiled_workflow_binding(node.id)

  if lifecycle not in ["READY", "COMPILED"]:
    record_admission_block(node.id, reason = "incompatible_lifecycle_state", lifecycle = lifecycle)
    return AdmissionResult(status = "blocked", reason = "incompatible_lifecycle_state")

  if compiled_workflow is null:
    record_admission_block(node.id, reason = "missing_compiled_workflow")
    return AdmissionResult(status = "blocked", reason = "missing_compiled_workflow")

  if has_active_pause_gate(node.id):
    record_admission_block(node.id, reason = "pause_gate_active")
    return AdmissionResult(status = "blocked", reason = "pause_gate_active")

  if has_incompatible_active_run(node.id):
    conflicting_run = load_active_run(node.id)
    record_admission_block(node.id, reason = "active_run_conflict", run_id = conflicting_run.id)
    return AdmissionResult(status = "blocked", reason = "active_run_conflict", run_id = conflicting_run.id)

  readiness = check_node_dependency_readiness(node.id)
  if readiness.status in ["blocked", "invalid", "impossible_wait"]:
    record_admission_block(node.id, reason = readiness.status, details = readiness)
    return AdmissionResult(status = "blocked", reason = readiness.status)

  begin_transaction()
  run = create_node_run(node.id, compiled_workflow.id)
  initialize_run_cursor(run.id, compiled_workflow.entry_subtask_id)
  mark_node_running(node.id, run.id)
  persist_workflow_event(
    node_version_id = node.id,
    node_run_id = run.id,
    event_type = "run_admitted",
    event_scope = "run",
    payload_json = { "compiled_workflow_id": compiled_workflow.id }
  )
  commit_transaction()

  return AdmissionResult(status = "admitted", node_run_id = run.id)
```

---

## Admission rules

A node may start only if:

- compiled workflow exists
- lifecycle state is compatible with running
- required dependencies are satisfied
- no blocking user gate is active
- no incompatible active run already exists

Recommended first-pass compatible lifecycle states:

- `READY`
- optionally `COMPILED` only if runtime policy allows immediate promotion during admission

Safer default:

- prefer explicit `READY`

---

## Failure paths

### Incompatible lifecycle

- reject or block admission from:
  - `DRAFT`
  - `COMPILE_FAILED`
  - `PAUSED_FOR_USER`
  - `FAILED_TO_PARENT`
  - `SUPERSEDED`
  - `CANCELLED`

### Missing compiled workflow

- block admission
- preserve missing-workflow reason explicitly

### Dependency blocker

- block admission without creating a run
- expose blocker details

### Active run conflict

- block admission
- do not create duplicate authoritative runs

---

## Pause/recovery behavior

- admission should not silently clear a pause gate
- interrupted admission transaction must not leave a half-created authoritative run

---

## CLI-visible expectations

Operators should be able to inspect:

- whether run start was admitted or blocked
- why admission was blocked
- active conflicting run if one exists
- dependency blocker details when relevant

---

## Pseudotests

### `blocks_compile_failed_node`

Given:

- lifecycle state is `COMPILE_FAILED`

Expect:

- admission is blocked
- no run is created

### `blocks_unsatisfied_dependencies`

Given:

- dependency readiness returns `blocked`

Expect:

- admission is blocked
- blocker details remain queryable

### `admits_ready_unblocked_node_and_initializes_cursor`

Given:

- lifecycle is `READY`
- compiled workflow exists
- no conflicting active run
- dependency readiness is `ready`

Expect:

- node run is created
- cursor is initialized
- node transitions to running state
