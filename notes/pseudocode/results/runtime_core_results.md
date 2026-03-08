# Runtime Core Results

## Suite summary

- `pass`: 16
- `partial`: 0
- `fail`: 0

---

### `compile_accepts_valid_workflow_inputs`

- Verdict: `pass`
- Simulated inputs:
  - `node_version_id = NV-100`
  - complete built-in, extension, and override YAML sets
  - no hook-order conflicts
- Simulated YAML reads:
  - built-in node/task/subtask definitions
  - project extension definitions
  - override definitions
  - project policy definitions
- Simulated DB reads:
  - `node_versions` for compile target
  - source-discovery metadata
- Logic path:
  - `compile_workflow` loads compile context
  - discovers sources
  - loads docs
  - resolves overrides
  - validates YAML
  - resolves policy
  - expands hooks
  - compiles immutable workflow
  - validates compiled graph
  - persists workflow transactionally
- Simulated DB writes:
  - `source_lineage`
  - resolved YAML snapshot
  - `compiled_workflows`
  - `compiled_tasks`
  - `compiled_subtasks`
  - readiness state on `node_versions`
- Forbidden-effects check:
  - no compile failure record created
  - no run admitted during compile

### `compile_rejects_invalid_override_target`

- Verdict: `pass`
- Simulated inputs:
  - override targets nonexistent task definition `task/foo`
- Simulated YAML reads:
  - built-in definitions
  - override file containing missing target reference
- Simulated DB reads:
  - `node_versions`
  - discovered source refs
- Logic path:
  - `compile_workflow` reaches `override_resolution`
  - `resolve_overrides` cannot resolve target
  - raises compile failure
- Simulated DB writes:
  - `compile_failures` with `failure_stage = override_resolution`
  - `failure_class = override_missing_target`
  - compile-failed node state marker
- Forbidden-effects check:
  - no compiled workflow persisted
  - no authoritative workflow hash updated

### `compile_rejects_invalid_dependency_graph`

- Verdict: `pass`
- Simulated inputs:
  - expanded workflow produces cyclic compiled dependency edge set
- Simulated YAML reads:
  - source YAML producing tasks/subtasks
  - hook definitions that insert invalid dependency edge
- Simulated DB reads:
  - compile target and source refs
- Logic path:
  - compile succeeds through hook expansion
  - `validate_compiled_dependency_graph` rejects cycle
  - failure is trapped by `compile_workflow`
- Simulated DB writes:
  - `compile_failures` with `failure_stage = compiled_graph_validation`
  - node compile-failed status
- Forbidden-effects check:
  - no authoritative compiled snapshot survives validation failure

### `admission_blocks_non_ready_node`

- Verdict: `pass`
- Simulated inputs:
  - node lifecycle state `COMPILE_FAILED`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - `node_versions` lifecycle state
  - compiled workflow binding presence
- Logic path:
  - `admit_node_run` loads authoritative node version
  - reads lifecycle state
  - lifecycle not in `["READY", "COMPILED"]`
  - records admission block with `reason = incompatible_lifecycle_state`
  - returns blocked result
- Simulated DB writes:
  - none required if admission is rejected
- Forbidden-effects check:
  - run should not be created

### `admission_blocks_unsatisfied_dependencies`

- Verdict: `pass`
- Simulated inputs:
  - node is otherwise ready
  - dependency blocker is unresolved
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - `node_versions`
  - dependency edges
  - authoritative dependency target states
- Logic path:
  - `admit_node_run` passes lifecycle/compiled-workflow checks
  - invokes `check_node_dependency_readiness`
  - readiness returns `blocked`
  - admission block recorded with blocker details
  - no run created
- Simulated DB writes:
  - likely none or a blocker-return payload only
- Forbidden-effects check:
  - no `node_runs` row should become authoritative

### `admission_allows_ready_unblocked_node`

- Verdict: `pass`
- Simulated inputs:
  - lifecycle `READY`
  - no active conflicting run
  - dependencies satisfied
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - `node_versions`
  - dependency state
  - active run existence
- Logic path:
  - `admit_node_run` loads authoritative node version
  - verifies lifecycle compatibility
  - verifies compiled workflow exists
  - sees no pause gate
  - sees no active run conflict
  - `check_node_dependency_readiness -> ready`
  - creates node run transactionally
  - initializes run cursor
  - marks node running
  - emits `run_admitted` workflow event
- Simulated DB writes:
  - expected `node_runs` creation
  - cursor initialization
- Forbidden-effects check:
  - no duplicate active run allowed

### `node_loop_advances_after_successful_subtask`

- Verdict: `pass`
- Simulated inputs:
  - current compiled subtask returns `ok`
  - acceptance checks pass
- Simulated YAML reads:
  - none; execution uses compiled workflow
- Simulated DB reads:
  - `node_runs`
  - run cursor state
  - `compiled_subtasks`
  - session binding
- Logic path:
  - `run_node_loop` loads run/session
  - creates/resumes attempt
  - `execute_compiled_subtask` dispatches handler
  - persists outputs
  - runs acceptance checks
  - marks attempt complete
  - advances cursor
- Simulated DB writes:
  - `subtask_attempts`
  - output snapshots
  - validation/review/test result rows if applicable
  - cursor advancement
- Forbidden-effects check:
  - no early cursor advancement before acceptance

### `node_loop_pauses_on_human_gate`

- Verdict: `pass`
- Simulated inputs:
  - handler returns `pause` with `pause_flag_name = user_approval_required`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - current run and subtask state
- Logic path:
  - `run_node_loop` receives `pause`
  - persists outputs if any
  - registers pause summary
  - marks subtask paused
  - transitions run to paused
  - records pause event
  - exits loop
- Simulated DB writes:
  - `summaries`
  - paused attempt state
  - run pause state
  - pause event
- Forbidden-effects check:
  - cursor does not advance
  - loop does not auto-resume

### `node_loop_finalizes_when_cursor_exhausted`

- Verdict: `pass`
- Simulated inputs:
  - `get_current_compiled_subtask(run.id) -> null`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - run state
  - current cursor
- Logic path:
  - `run_node_loop` detects no remaining subtask
  - invokes `finalize_completed_workflow`
  - returns completed result
- Simulated DB writes:
  - finalization result
  - terminal run/node status
- Forbidden-effects check:
  - no phantom subtask attempt created

### `subtask_failure_records_summary_and_blocks_progress`

- Verdict: `pass`
- Simulated inputs:
  - current handler returns `failed`
  - `failure_class = validation_failure`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - current run/subtask/attempt state
  - retry policy
- Logic path:
  - `run_node_loop` persists any outputs
  - registers failure summary
  - marks attempt failed
  - invokes `handle_subtask_failure`
  - returns decision instead of advancing
- Simulated DB writes:
  - failed `subtask_attempt`
  - `summaries`
  - failure counters/decision history
- Forbidden-effects check:
  - cursor remains on failing subtask unless retry logic later reuses same position

### `retry_budget_exhaustion_escalates_to_parent_or_operator`

- Verdict: `pass`
- Simulated inputs:
  - repeated failure attempts exhaust retry budget and thresholds
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - retry policy
  - current failure counters
  - parent relationship
- Logic path:
  - `handle_subtask_failure` classifies failure
  - increments counters
  - `exceeds_hard_stop_thresholds(...) == true`
  - records failure decision
  - transitions run to paused or fail-to-parent according to policy
- Simulated DB writes:
  - updated counters
  - failure decision record
  - paused run state or parent escalation payload
- Forbidden-effects check:
  - no infinite autonomous retry loop continues past budget

### `recovery_reuses_existing_healthy_session_when_safe`

- Verdict: `pass`
- Simulated inputs:
  - active run exists
  - session classifies as `healthy`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - active run
  - active primary session
  - cursor state
  - heartbeat status
  - git state
- Logic path:
  - `recover_interrupted_run` records recovery attempt
  - sees `is_resumable = true`
  - no git mismatch
  - no duplicate session ambiguity
  - `session_class in [healthy, detached]`
  - refreshes existing session and reloads cursor context
- Simulated DB writes:
  - recovery-attempt event
  - recovery-success event
  - refreshed session binding metadata
- Forbidden-effects check:
  - no replacement session created

### `recovery_creates_replacement_session_when_tmux_is_lost`

- Verdict: `pass`
- Simulated inputs:
  - resumable run
  - primary session lost
  - tmux missing
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - active run
  - session record
  - cursor state
  - git state
- Logic path:
  - recovery attempt recorded
  - session classifies as `lost`
  - replacement session is created and rebound
  - current cursor context reloaded
- Simulated DB writes:
  - recovery-attempt event
  - replacement `sessions` row
  - replacement bind event
  - recovery success event
- Forbidden-effects check:
  - no cursor reset to guessed state

### `recovery_refuses_non_resumable_run`

- Verdict: `pass`
- Simulated inputs:
  - `is_resumable = false`
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - active run
  - run status flags
- Logic path:
  - recovery attempt recorded
  - `state.is_resumable is false`
  - recovery rejected
- Simulated DB writes:
  - recovery-attempt event
  - rejection record
- Forbidden-effects check:
  - no replacement session created
  - no silent resume

### `all_critical_runtime_transitions_are_queryable`

- Verdict: `pass`
- Simulated inputs:
  - one compile
  - one successful subtask
  - pause
  - recovery
  - completion
- Simulated YAML reads:
  - compile-time source docs only during initial compile
- Simulated DB reads:
  - all runtime/read-model surfaces
- Logic path:
  - the package explicitly models most transitions
  - compile, run, subtask, pause, recovery, parent-decision, cutover, and completion all have durable representations
  - `workflow_events` state machine now bounds event-worthy transitions and CLI visibility
- Simulated DB writes:
  - `compile_failures` or compile success equivalents
  - `node_runs`
  - `subtask_attempts`
  - `summaries`
  - `sessions`
  - pause/recovery events
  - `workflow_events`
- Forbidden-effects check:
  - hidden state is mostly blocked by design

### `failed_compile_never_admits_run`

- Verdict: `pass`
- Simulated inputs:
  - compile previously failed for node version
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - `compile_failures`
  - node lifecycle state
  - run existence
- Logic path:
  - compile module marks compile-failed state
  - `admit_node_run` loads lifecycle state
  - rejects admission with `incompatible_lifecycle_state`
  - no run created
- Simulated DB writes:
  - none expected if correctly rejected
- Forbidden-effects check:
  - no run/session should bind to failed version
