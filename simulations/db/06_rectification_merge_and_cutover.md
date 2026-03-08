# DB Simulation: Rectification, Merge, And Cutover

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/git_rectification_spec_v2.md`
- `notes/cutover_policy_note.md`

## Scenario

`task_greeting_v1` is superseded by `task_greeting_v2`, then parent `plan_v1` is rebuilt as `plan_v2`.

## Simulated durable operations

### Step 1: insert superseding child version

```yaml
insert:
  table: node_versions
  values:
    id: task_greeting_v2
    logical_node_id: task_greeting_logical
    parent_node_version_id: plan_v1
    node_kind: task
    version_number: 2
    supersedes_node_version_id: task_greeting_v1
    status: DRAFT
```

```yaml
update:
  table: logical_node_current_versions
  where:
    logical_node_id: task_greeting_logical
  set:
    latest_created_node_version_id: task_greeting_v2
```

### Step 2: insert `rebuild_events`

```yaml
insert:
  table: rebuild_events
  values:
    id: reb_001
    old_node_version_id: task_greeting_v1
    new_node_version_id: task_greeting_v2
    trigger_reason: user_requested_regeneration
```

### Step 3: insert candidate parent version

```yaml
insert:
  table: node_versions
  values:
    id: plan_v2
    logical_node_id: plan_logical
    node_kind: plan
    version_number: 2
    supersedes_node_version_id: plan_v1
    status: RECTIFYING_UPSTREAM
```

```yaml
update:
  table: logical_node_current_versions
  where:
    logical_node_id: plan_logical
  set:
    latest_created_node_version_id: plan_v2
```

### Step 3A: insert candidate lineage edges

```yaml
inserts:
  - table: node_version_lineage
    values:
      parent_node_version_id: plan_v1
      child_node_version_id: task_greeting_v1
      lineage_scope: authoritative
  - table: node_version_lineage
    values:
      parent_node_version_id: plan_v2
      child_node_version_id: task_greeting_v2
      lineage_scope: candidate
```

### Step 4: insert `merge_events`

```yaml
inserts:
  - table: merge_events
    values:
      id: mevt_001
      parent_node_version_id: plan_v2
      child_node_version_id: task_parser_v1
      child_final_commit_sha: parser111
      parent_commit_before: planseed001
      parent_commit_after: planmerge100
      merge_order: 1
  - table: merge_events
    values:
      id: mevt_002
      parent_node_version_id: plan_v2
      child_node_version_id: task_greeting_v2
      child_final_commit_sha: greet222
      parent_commit_before: planmerge100
      parent_commit_after: planmerge200
      merge_order: 2
```

### Step 5: authoritative cutover

The DB now reflects cutover through:

- `logical_node_current_versions.authoritative_node_version_id`
- authoritative/candidate lineage edges
- superseded version statuses
- `workflow_events`

```yaml
updates:
  - table: logical_node_current_versions
    where:
      logical_node_id: task_greeting_logical
    set:
      authoritative_node_version_id: task_greeting_v2
  - table: logical_node_current_versions
    where:
      logical_node_id: plan_logical
    set:
      authoritative_node_version_id: plan_v2
```

```yaml
insert:
  table: workflow_events
  values:
    node_version_id: plan_v2
    event_type: cutover_completed
    event_scope: cutover
    payload_json: "{old_authoritative:'plan_v1',new_authoritative:'plan_v2'}"
```

## Logic issues exposed

1. Candidate-lineage linkage is now explicit, but the coexistence of `parent_node_version_id` and `node_version_lineage` still requires careful implementation discipline to avoid accidental misuse of the simpler field during rebuilds.
