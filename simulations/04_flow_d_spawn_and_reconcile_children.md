# Flow D: Spawn And Reconcile Children

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/git_rectification_spec_v2.md`

## Scenario

A parent `plan` has a layout with two children:

- `task_a`
- `task_b`, which depends on `task_a`

## Full task flow

### Step 1: validate layout before materialization

Checks:

- unique child IDs
- valid kinds/tiers
- valid dependency references
- no cycles
- no self-dependencies

### Step 2: materialize children

```text
materialize_layout_children(parent=plan_v2, layout=.ai/layouts/plan_v2.yaml)
```

Simulated result:

```json
{
  "status": "OK",
  "children_created": [
    {"node_version_id": "task_a_v1", "state": "COMPILED"},
    {"node_version_id": "task_b_v1", "state": "COMPILED"}
  ],
  "dependency_edges_created": [
    {"from": "task_b_v1", "to": "task_a_v1", "type": "sibling"}
  ]
}
```

### Step 3: schedule children

Initial classification:

```yaml
task_a_v1: ready
task_b_v1: blocked_on_dependency
```

If `auto_run_children` is enabled:

- daemon starts `task_a_v1`
- `task_b_v1` remains blocked

### Step 4: reschedule after dependency clears

When `task_a_v1` completes:

```yaml
task_a_v1: complete
task_b_v1: ready
```

Daemon starts `task_b_v1`.

### Step 5: wait for required children

The parent remains in `wait_for_children` until all required children are `COMPLETE`.

### Step 6: reconcile parent

Parent subtasks:

1. `reset_to_seed`
2. `merge_children`
3. `record_merge_metadata`
4. parent-local reconcile step

Simulated merge:

```json
{
  "status": "OK",
  "merge_order": ["task_a_v1", "task_b_v1"],
  "head_after_merge": "planmerge900"
}
```

## Logic issues exposed

1. The library plan defines `wait_for_dependencies`, but the default node-kind flows omit it. That makes sibling-dependency waiting partly a scheduler concern and partly a task concern without one canonical location.
2. Parent reconcile behavior is still much less concretely specified than rectification behavior.

