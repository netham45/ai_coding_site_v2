# DB Simulation: Run Admission And Subtask Execution

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/state_value_catalog.md`

## Scenario

Admit a run for `plan_v1`, start the first subtask, complete it, and advance the cursor.

## Simulated durable operations

### Step 1: insert `node_runs`

```yaml
insert:
  table: node_runs
  values:
    id: run_plan_v1_1
    node_version_id: plan_v1
    run_number: 1
    trigger_reason: operator_start
    run_status: RUNNING
    compiled_workflow_id: cw_plan_v1
```

### Step 2: insert `node_run_state`

```yaml
insert:
  table: node_run_state
  values:
    node_run_id: run_plan_v1_1
    lifecycle_state: RUNNING
    current_task_id: ct_001
    current_compiled_subtask_id: cst_001
    current_subtask_attempt: 1
    last_completed_compiled_subtask_id: null
    execution_cursor_json: "{task:1,subtask:1}"
    is_resumable: true
```

### Step 3: insert primary `sessions`

```yaml
insert:
  table: sessions
  values:
    id: sess_plan_v1_1
    node_version_id: plan_v1
    node_run_id: run_plan_v1_1
    session_role: primary
    provider: codex
    tmux_session_name: plan_v1_main
    status: ACTIVE
```

### Step 4: start subtask attempt

```yaml
insert:
  table: subtask_attempts
  values:
    id: att_001
    node_run_id: run_plan_v1_1
    compiled_subtask_id: cst_001
    attempt_number: 1
    status: STARTED
    started_at: now()
```

### Step 5: record prompt and heartbeat

```yaml
inserts:
  - table: prompts
    values:
      id: prm_001
      node_run_id: run_plan_v1_1
      compiled_subtask_id: cst_001
      prompt_role: current_subtask
      content_hash: prompt_hash_001
  - table: session_events
    values:
      id: sevt_001
      session_id: sess_plan_v1_1
      event_type: heartbeat
```

### Step 6: complete subtask attempt

```yaml
update:
  table: subtask_attempts
  where:
    id: att_001
  set:
    status: SUCCEEDED
    output_json: "{status:ok}"
    summary: Loaded request context
    ended_at: now()
```

### Step 7: advance cursor

```yaml
update:
  table: node_run_state
  where:
    node_run_id: run_plan_v1_1
  set:
    current_compiled_subtask_id: cst_002
    current_subtask_attempt: 1
    last_completed_compiled_subtask_id: cst_001
    execution_cursor_json: "{task:1,subtask:2}"
```

## Logic issues exposed

1. `subtask_attempts.status` includes both `STARTED` and `RUNNING` in the state catalog, but the practical difference is not yet clear.
