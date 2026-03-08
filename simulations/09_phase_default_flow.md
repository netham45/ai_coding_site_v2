# Phase Default Flow

Source:

- `notes/default_yaml_library_plan.md`

## Proposed task sequence

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

## Full task transcript

This is the same structural sequence as epic, but its children are `plan` nodes instead of `phase` nodes.

Main difference in practice:

- `generate_child_layout` targets plans
- reconciliation merges plan finals
- tests/reviews are scoped to the phase

## Logic issues exposed

1. The spec currently treats epic and phase flows as nearly identical. That may be acceptable, but phase-specific policy distinctions are not yet reflected in the built-in flow definitions.
