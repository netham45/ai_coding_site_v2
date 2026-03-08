# Runtime Core Pseudotests

## Purpose

These pseudotests validate the first-pass runtime spine:

- `compile_workflow(...)`
- `admit_node_run(...)`
- `run_node_loop(...)`
- `execute_compiled_subtask(...)`
- `handle_subtask_failure(...)`
- `recover_interrupted_run(...)`

Some modules are not yet authored in this folder. These tests still define the behaviors they must satisfy.

---

## Test format

Each case defines:

- scenario
- preconditions
- action
- expected durable effects
- expected operator-visible results

---

## Compile pipeline

### `compile_accepts_valid_workflow_inputs`

Scenario:

- a node version has complete built-in, extension, and override inputs
- all YAML validates
- hooks expand without violating canonical order

Action:

- run `compile_workflow(node_version_id)`

Expected durable effects:

- resolved YAML lineage is persisted
- compiled workflow, tasks, and subtasks are persisted
- node version becomes ready for run admission

Expected operator-visible results:

- compile status reports success
- compiled workflow can be queried

### `compile_rejects_invalid_override_target`

Scenario:

- an override targets a nonexistent task definition

Action:

- run `compile_workflow(node_version_id)`

Expected durable effects:

- compile failure record is written with stage `override_resolution`
- node version remains non-runnable

Expected operator-visible results:

- compile failure query shows target family and target ID

### `compile_rejects_invalid_dependency_graph`

Scenario:

- hook expansion or source definitions produce a cyclic or otherwise illegal compiled dependency graph

Action:

- run `compile_workflow(node_version_id)`

Expected durable effects:

- no compiled workflow becomes authoritative
- compile failure is recorded against graph validation

Expected operator-visible results:

- failure is inspectable without reading raw logs

---

## Run admission

### `admission_blocks_non_ready_node`

Scenario:

- node version is in compile-failed or draft-like state

Action:

- run `admit_node_run(node_id)`

Expected durable effects:

- no node run is created

Expected operator-visible results:

- admission response explains the blocking state

### `admission_blocks_unsatisfied_dependencies`

Scenario:

- compiled workflow exists
- at least one required child or sibling dependency is incomplete

Action:

- run `admit_node_run(node_id)`

Expected durable effects:

- no active run is created
- dependency-block reason is recorded or returned

Expected operator-visible results:

- blocker query shows the unsatisfied dependency

### `admission_allows_ready_unblocked_node`

Scenario:

- node version is ready
- there is no conflicting active run
- dependencies are satisfied

Action:

- run `admit_node_run(node_id)`

Expected durable effects:

- node run is created
- cursor is initialized
- primary session binding becomes possible

---

## Canonical node loop

### `node_loop_advances_after_successful_subtask`

Scenario:

- current compiled subtask is executable
- handler returns success

Action:

- run one iteration of `run_node_loop(node_id)`

Expected durable effects:

- subtask attempt is marked started then completed
- outputs are persisted
- validations run
- cursor advances to the next compiled subtask

### `node_loop_pauses_on_human_gate`

Scenario:

- current subtask determines that user input or approval is required

Action:

- run one iteration of `run_node_loop(node_id)`

Expected durable effects:

- pause summary is registered
- run transitions to paused state
- cursor does not advance

Expected operator-visible results:

- pause reason and current subtask remain queryable

### `node_loop_finalizes_when_cursor_exhausted`

Scenario:

- no current compiled subtask remains

Action:

- run `run_node_loop(node_id)`

Expected durable effects:

- finalization is invoked
- node reaches completed or next canonical post-run state

---

## Failure handling

### `subtask_failure_records_summary_and_blocks_progress`

Scenario:

- current subtask fails with a structured failure summary

Action:

- run one iteration of `run_node_loop(node_id)`

Expected durable effects:

- failure summary is registered
- failure handler is invoked
- cursor does not advance past the failing subtask

Expected operator-visible results:

- current failure is inspectable

### `retry_budget_exhaustion_escalates_to_parent_or_operator`

Scenario:

- the same subtask or child failure recurs until retry policy is exhausted

Action:

- invoke `handle_subtask_failure(...)` repeatedly according to policy

Expected durable effects:

- final failure state is recorded
- escalation decision is recorded

Expected operator-visible results:

- parent escalation or manual intervention requirement is visible

---

## Recovery

### `recovery_reuses_existing_healthy_session_when_safe`

Scenario:

- node run is active
- tmux session exists
- session heartbeat is stale enough to trigger review but still recoverable

Action:

- run `recover_interrupted_run(node_id)`

Expected durable effects:

- existing session binding is preserved or refreshed
- cursor remains on the current compiled subtask

Expected operator-visible results:

- recovery path shows reuse rather than replacement

### `recovery_creates_replacement_session_when_tmux_is_lost`

Scenario:

- node run is resumable
- tmux session is gone
- durable cursor and compiled workflow state exist

Action:

- run `recover_interrupted_run(node_id)`

Expected durable effects:

- replacement session is created and bound
- recovery event is recorded
- current work resumes from durable cursor state rather than guesswork

Expected operator-visible results:

- old and replacement session lineage can be inspected

### `recovery_refuses_non_resumable_run`

Scenario:

- run is marked non-resumable by policy or terminal state

Action:

- run `recover_interrupted_run(node_id)`

Expected durable effects:

- no new session is created

Expected operator-visible results:

- operator sees that recovery was rejected and why

---

## Cross-cutting auditability

### `all_critical_runtime_transitions_are_queryable`

Scenario:

- a node compiles, runs one successful subtask, pauses, resumes, then completes

Action:

- query the system only through intended CLI/operator surfaces

Expected durable effects:

- compile outcome, run creation, subtask attempt history, pause event, recovery event, and final status all exist durably

Expected operator-visible results:

- no critical transition depends on hidden in-memory state

### `failed_compile_never_admits_run`

Scenario:

- compile fails for a node version

Action:

- attempt admission and session binding anyway

Expected durable effects:

- no run or primary session becomes authoritative for that failed version

Expected operator-visible results:

- blocker is the compile failure, not a generic admission denial
