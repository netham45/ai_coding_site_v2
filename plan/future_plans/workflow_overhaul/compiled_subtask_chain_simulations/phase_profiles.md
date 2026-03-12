# Phase Profile Simulations

## `phase.discovery`

- Kind: `phase`
- Child target: `plan`
- Required roles: `context`, `boundary_definition`, `verification_mapping`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until the discovery plan set exists.

## `phase.implementation`

- Kind: `phase`
- Child target: `plan`
- Required roles: `execution`, `verification`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until implementation and verification plans are materialized.

## `phase.documentation`

- Kind: `phase`
- Child target: `plan`
- Required roles: `authoring`, `verification`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until the authoring and verification plans exist.

## `phase.e2e`

- Kind: `phase`
- Child target: `plan`
- Required roles: `execution`, `verification`, `remediation`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until real-proof plans are materialized and later merged.

## `phase.review`

- Kind: `phase`
- Child target: `plan`
- Required roles: `evidence`, `findings`, `handoff`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until review and handoff plans are materialized.

## `phase.remediation`

- Kind: `phase`
- Child target: `plan`
- Required roles: `fix`, `status_alignment`, `proof`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_plan_layout`
  4. `validate_role_coverage`
  5. `materialize_plan_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until remediation plans and proof plans exist.
