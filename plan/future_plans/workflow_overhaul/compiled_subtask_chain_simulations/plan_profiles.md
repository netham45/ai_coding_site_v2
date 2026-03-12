# Plan Profile Simulations

## `plan.authoring`

- Kind: `plan`
- Child target: `task`
- Required roles: `author`, `review`, `finalize`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_task_layout`
  4. `validate_role_coverage`
  5. `materialize_task_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until author/review/finalize tasks are spawned and later closed.

## `plan.execution`

- Kind: `plan`
- Child target: `task`
- Required roles: `implement`, `verify`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_task_layout`
  4. `validate_role_coverage`
  5. `materialize_task_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until implementation and verification tasks exist.

## `plan.verification`

- Kind: `plan`
- Child target: `task`
- Required roles: `execute_checks`, `assess_results`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_task_layout`
  4. `validate_role_coverage`
  5. `materialize_task_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until execution and assessment tasks are spawned and later merged.
