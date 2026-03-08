# Parent Child Failure Decision Flow

Sources:

- `notes/parent_failure_decision_spec.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

## Scenario

Parent `plan_v1` has two children:

- `task_a_v1` already `COMPLETE`
- `task_b_v1` fails during `test_node`

The parent must record the failure, classify it, check thresholds, and decide the next step.

## Starting state reads

Daemon reads:

1. `node_children` for `plan_v1`
2. `node_runs` for latest child runs
3. `node_run_state` for parent `run_plan_v1_1`
4. `node_run_state` for child `run_task_b_v1_1`
5. `subtask_attempts` for child failing subtask
6. `test_results` for `task_b_v1`
7. parent policy values from compiled workflow or resolved node policy:
   - `child_failure_threshold_total`
   - `child_failure_threshold_consecutive`
   - `child_failure_threshold_per_child`

## Child-side failure record

### Child CLI and runtime boundary

The child runtime finishes the failing compiled subtask and records failure before the parent reacts.

Relevant read paths after failure:

```text
ai-tool node run show --node task_b_v1
ai-tool subtask attempts --node task_b_v1
ai-tool node events --node task_b_v1
```

### Child DB writes

1. `subtask_attempts`
   - update current failing subtask attempt:
     - `status = FAILED`
     - `summary = Focused pytest failed`
     - `output_json` contains failure payload
2. `test_results`
   - insert:
     - `node_version_id = task_b_v1`
     - `node_run_id = run_task_b_v1_1`
     - `compiled_subtask_id = cst_task_b_test`
     - `status = FAIL`
     - `summary = 2 tests failed`
3. `summaries`
   - insert child failure summary
4. `node_run_state`
   - update:
     - `lifecycle_state = FAILED_TO_PARENT`
     - `current_compiled_subtask_id = cst_task_b_test`
5. `node_runs`
   - update:
     - `run_status = FAILED`
     - `ended_at = now()`
6. `workflow_events`
   - insert child failed-to-parent event

## Parent decision sequence

### CLI boundary

Assumed or intended operator-visible paths:

```text
ai-tool node events --node plan_v1
ai-tool node decision-history --node plan_v1
ai-tool node blockers --node plan_v1
ai-tool node pause-state --node plan_v1
```

### Step 1: record failure impact

Parent reads:

1. child failure class from latest child summary or test result
2. existing parent counters from `node_run_state`

Parent writes:

1. `node_run_state`
   - update parent row:
     - `failure_count_from_children = previous + 1`
     - `failure_count_consecutive = previous + 1`
2. `node_run_child_failure_counters`
   - upsert row for `task_b_v1`:
     - `failure_count = previous + 1`
     - `last_failure_class = test_failure`
2. `workflow_events`
   - insert `child_failure_recorded`
3. `summaries`
   - insert parent-facing impact summary

### Step 2: classify failure

Parent matches:

1. failed stage = `test_node`
2. child summary indicates test failure
3. no evidence of dependency ambiguity or layout invalidity

Classification:

```yaml
failure_class: test_failure
retryable: true
```

Parent writes:

1. `workflow_events`
   - insert `child_failure_classified`

### Step 3: threshold check

Parent compares:

- `failure_count_from_children` against `child_failure_threshold_total`
- `failure_count_consecutive` against `child_failure_threshold_consecutive`
- per-child count for `task_b_v1` against `child_failure_threshold_per_child`

Result for this simulation:

- no threshold exceeded

Parent writes:

1. `workflow_events`
   - insert `child_failure_threshold_check_passed`

### Step 4: choose retry

Parent verifies:

1. failure class is retryable
2. child retry budget remains
3. current layout is still believed valid
4. no policy forbids retry

Decision:

```yaml
decision: retry_child
target_child: task_b_v1
reason: test failure appears local and retry budget remains
```

Parent writes:

1. `workflow_events`
   - insert `parent_retry_child`
2. `summaries`
   - insert decision summary

### Step 5: child retry start

Daemon starts a new child run or retry path depending on implementation policy.

If same child version gets another run:

1. `node_runs`
   - insert `run_task_b_v1_2`
2. `node_run_state`
   - insert new running row
3. `sessions`
   - insert new primary session or replacement session
4. `session_events`
   - insert `bound`
5. `workflow_events`
   - insert retry run started

If retry is modeled as another attempt in same run, then instead:

1. `subtask_attempts`
   - insert attempt 2 for same compiled subtask
2. `node_run_state`
   - update current attempt number

The notes are clearer on retry policy than on whether child retry means:

- same run, new attempt
- or new run

This simulation assumes a new child run for simpler operator visibility.

## Failure-to-pause variant

If retry fails again and threshold is exceeded:

Parent writes:

1. `node_run_state`
   - update `lifecycle_state = PAUSED_FOR_USER`
   - set `pause_flag_name`
2. `summaries`
   - insert structured pause summary listing:
     - failed child
     - retries attempted
     - likely root cause
     - suggested actions
3. `workflow_events`
   - insert `pause_entered`

CLI result:

```text
ai-tool node pause-state --node plan_v1
```

```yaml
node_version_id: plan_v1
lifecycle_state: PAUSED_FOR_USER
pause_flag_name: child_failure_threshold_exceeded
summary_ref: summary_plan_pause_1
```

## Result

This simulation shows the exact compositional rule:

- child fails locally first
- parent records and classifies
- parent decides retry or pause
- no direct child-to-grandparent escalation occurs

## Hole still visible

The specs are now aligned on a dedicated per-child counter table, but the exact event taxonomy for parent decision history still needs disciplined implementation.
