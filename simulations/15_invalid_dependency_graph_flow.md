# Invalid Dependency Graph Flow

Sources:

- `notes/invalid_dependency_graph_handling.md`
- `notes/child_materialization_and_scheduling.md`

## Scenario

A layout contains a cycle:

- `task_a` depends on `task_b`
- `task_b` depends on `task_a`

## Full task flow

1. `generate_child_layout` writes the layout
2. `review_child_layout` may pass or miss the structural issue
3. `layout validate` detects the cycle
4. `spawn_children` is blocked
5. parent must revise layout or pause

## Simulated validation result

```json
{
  "status": "FAIL",
  "dependency_validation": "invalid_cycle",
  "summary": "Child dependency graph contains a cycle between task_a and task_b."
}
```

## Logic issues exposed

1. There is no fully frozen built-in task path yet for “dependency validation failed, should we auto-revise or pause”.

