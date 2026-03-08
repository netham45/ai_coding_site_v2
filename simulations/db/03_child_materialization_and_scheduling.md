# DB Simulation: Child Materialization And Scheduling

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/invalid_dependency_graph_handling.md`

## Scenario

A parent `plan_v2` materializes two task children from a validated layout. `task_b_v1` depends on `task_a_v1`.

## Simulated durable operations

### Step 1: insert child `node_versions`

```yaml
inserts:
  - table: node_versions
    values:
      id: task_a_v1
      logical_node_id: task_a_logical
      parent_node_version_id: plan_v2
      tier: task
      node_kind: task
      status: COMPILED
      version_number: 1
  - table: node_versions
    values:
      id: task_b_v1
      logical_node_id: task_b_logical
      parent_node_version_id: plan_v2
      tier: task
      node_kind: task
      status: COMPILED
      version_number: 1
```

### Step 2: insert `node_children`

```yaml
inserts:
  - parent_node_version_id: plan_v2
    child_node_version_id: task_a_v1
    ordinal: 1
  - parent_node_version_id: plan_v2
    child_node_version_id: task_b_v1
    ordinal: 2
```

### Step 3: insert `node_dependencies`

```yaml
insert:
  table: node_dependencies
  values:
    id: dep_001
    node_version_id: task_b_v1
    depends_on_node_version_id: task_a_v1
    dependency_type: sibling
    required_state: COMPLETE
```

### Step 4: scheduling snapshot

There is no canonical table for scheduling snapshots in the core DB spec, so the daemon must derive schedulability from:

- child lifecycle state
- dependency rows
- active runs

Derived classification:

```yaml
task_a_v1: ready
task_b_v1: blocked_on_dependency
```

### Step 5: persist child authority mode

```yaml
insert:
  table: parent_child_authority
  values:
    parent_node_version_id: plan_v2
    authority_mode: layout_authoritative
    authoritative_layout_hash: layout_hash_plan_v2
```

## Logic issues exposed

1. The scheduling note explicitly suggests optional history tables like `layout_materializations` and `child_schedule_snapshots`, but those are not in the canonical DB spec yet.
