# DB Simulation: Session Recovery And Child Sessions

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/session_recovery_appendix.md`
- `notes/child_session_mergeback_contract.md`

## Scenario A

Primary session is lost and replaced.

## Simulated durable operations

### Step 1: mark old session stale or invalid

```yaml
update:
  table: sessions
  where:
    id: sess_task_v1_1
  set:
    status: INVALIDATED
    ended_at: now()
```

### Step 2: insert replacement session

```yaml
insert:
  table: sessions
  values:
    id: sess_task_v1_2
    node_version_id: task_v1
    node_run_id: run_task_v1_1
    session_role: primary
    provider: codex
    tmux_session_name: task_v1_recovery
    status: ACTIVE
```

### Step 3: record session events

```yaml
inserts:
  - table: session_events
    values:
      session_id: sess_task_v1_1
      event_type: invalidated
  - table: session_events
    values:
      session_id: sess_task_v1_2
      event_type: replacement_created
  - table: workflow_events
    values:
      node_version_id: task_v1
      node_run_id: run_task_v1_1
      event_type: replacement_session_created
      event_scope: recovery
```

## Scenario B

Pushed child session returns bounded work.

### Step 4: insert child session

```yaml
insert:
  table: sessions
  values:
    id: child_sess_1
    node_version_id: plan_v1
    node_run_id: run_plan_v1_1
    session_role: pushed_child
    parent_session_id: sess_plan_v1_1
    provider: codex
    status: ACTIVE
```

### Step 5: persist child result

```yaml
insert:
  table: child_session_results
  values:
    id: csr_001
    child_session_id: child_sess_1
    parent_compiled_subtask_id: cst_plan_003
    status: success
    result_json: "{summary:'repo scan complete'}"
```

## Logic issues exposed

1. Recovery decisions now have a canonical event home, but the exact boundary between `session_events` and `workflow_events` still needs disciplined implementation.
