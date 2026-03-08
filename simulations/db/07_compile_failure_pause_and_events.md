# DB Simulation: Compile Failure, Pause, And Workflow Events

Sources:

- `notes/compile_failure_persistence.md`
- `notes/pause_workflow_event_persistence.md`
- `notes/database_schema_spec_v2.md`

## Scenario A

Compilation fails due to override ambiguity.

### Simulated durable operation

```yaml
insert:
  table: compile_failures
  values:
    id: cf_001
    node_version_id: plan_v8
    failure_stage: override_resolution
    failure_class: override_merge_conflict
    summary: Two overrides produced conflicting replacement semantics
```

Possible paired node update:

```yaml
update:
  table: node_versions
  where:
    id: plan_v8
  set:
    status: COMPILE_FAILED
```

## Scenario B

A node enters `PAUSED_FOR_USER` after review failure.

### Current canonical DB story

Guaranteed durable pieces:

- `node_run_state.pause_flag_name`
- `summaries`
- possibly `session_events`

Recommended but not fully canonical:

- none for the event structure itself; `workflow_events` is now canonical

### Simulated pause row changes

```yaml
update:
  table: node_run_state
  where:
    node_run_id: run_task_v1_1
  set:
    lifecycle_state: PAUSED_FOR_USER
    pause_flag_name: review_revision_required
```

```yaml
insert:
  table: summaries
  values:
    id: sum_pause_001
    node_version_id: task_v1
    node_run_id: run_task_v1_1
    summary_type: pause
    content: Review failed twice; user input required
```

## Logic issues exposed

1. Compile failures have a dedicated table, but the exact query/view strategy that combines compile failures with current node status still needs more concrete read-model design.
