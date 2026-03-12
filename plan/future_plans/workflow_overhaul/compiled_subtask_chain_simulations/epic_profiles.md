# Epic Profile Simulations

## `epic.planning`

- Kind: `epic`
- Child target: `phase`
- Required roles: `requirements`, `architecture`, `planning`, `verification_mapping`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_phase_layout`
  4. `validate_role_coverage`
  5. `materialize_phase_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block `merge_children` or `complete` until required phase roles are materialized and later child closure conditions are satisfied.
- Expected closure: an inspectable planning-phase tree with durable role coverage and parent summary.

## `epic.feature`

- Kind: `epic`
- Child target: `phase`
- Required roles: `discovery`, `implementation`, `documentation`, `e2e`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_phase_layout`
  4. `validate_role_coverage`
  5. `materialize_phase_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion with `children_required_before_completion` until the required phase set exists.
- Expected closure: a full feature-delivery phase tree that preserves docs and real-E2E bands structurally.

## `epic.review`

- Kind: `epic`
- Child target: `phase`
- Required roles: `scope_freeze`, `review`, `remediation`, `re_review`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_phase_layout`
  4. `validate_role_coverage`
  5. `materialize_phase_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until the review/remediation/re-review structure exists and children close honestly.
- Expected closure: a review lifecycle tree with traceable findings and remediation handoff.

## `epic.documentation`

- Kind: `epic`
- Child target: `phase`
- Required roles: `inventory`, `authoring`, `verification`, `remediation`
- Simulated compiled subtask chain:
  1. `load_workflow_brief`
  2. `review_required_child_roles`
  3. `compose_phase_layout`
  4. `validate_role_coverage`
  5. `materialize_phase_children`
  6. `confirm_child_spawn_summary`
  7. `wait_for_children`
  8. `merge_children`
  9. `publish_parent_summary`
- Main gate: block completion until documentation lifecycle bands are present and child outputs are merged.
- Expected closure: a documentation lifecycle tree with explicit verification and remediation bands.
