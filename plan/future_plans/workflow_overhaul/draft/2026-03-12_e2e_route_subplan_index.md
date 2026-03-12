# Workflow Overhaul E2E Route Subplan Index

## Purpose

Provide a deeper implementation-sized breakdown for each workflow-overhaul E2E route so route planning can be executed in smaller batches.

## Structure

Each route now has file-per-child plans under `e2e_route_subplans/` for setup, happy-path assertions, adversarial checks, and inspection/traceability obligations.

## Route Families

### 00 Parentless Profile Start

- `e2e_route_subplans/00a_route_startup_matrix.md`
- `e2e_route_subplans/00b_happy_path_start_assertions.md`
- `e2e_route_subplans/00c_blocked_start_assertions.md`
- `e2e_route_subplans/00d_inspection_and_traceability.md`

### 01 Planning Ladder

- `e2e_route_subplans/01a_planning_route_setup.md`
- `e2e_route_subplans/01b_planning_happy_path.md`
- `e2e_route_subplans/01c_planning_blocked_assertions.md`
- `e2e_route_subplans/01d_planning_inspection_traceability.md`

### 02 Feature Delivery Ladder

- `e2e_route_subplans/02a_feature_delivery_route_setup.md`
- `e2e_route_subplans/02b_feature_delivery_happy_path.md`
- `e2e_route_subplans/02c_feature_delivery_blocked_assertions.md`
- `e2e_route_subplans/02d_feature_delivery_inspection_traceability.md`

### 03 Review And Remediation Ladder

- `e2e_route_subplans/03a_review_remediation_route_setup.md`
- `e2e_route_subplans/03b_review_remediation_happy_path.md`
- `e2e_route_subplans/03c_review_remediation_blocked_assertions.md`
- `e2e_route_subplans/03d_review_remediation_inspection_traceability.md`

### 04 Documentation Ladder

- `e2e_route_subplans/04a_documentation_route_setup.md`
- `e2e_route_subplans/04b_documentation_happy_path.md`
- `e2e_route_subplans/04c_documentation_blocked_assertions.md`
- `e2e_route_subplans/04d_documentation_inspection_traceability.md`

### 05 Blocked Completion Before Spawn

- `e2e_route_subplans/05a_completion_before_spawn_setup.md`
- `e2e_route_subplans/05b_completion_before_spawn_happy_path.md`
- `e2e_route_subplans/05c_completion_before_spawn_blocked_assertions.md`
- `e2e_route_subplans/05d_completion_before_spawn_inspection_traceability.md`

### 06 Blocked Step Skip

- `e2e_route_subplans/06a_step_skip_route_setup.md`
- `e2e_route_subplans/06b_step_skip_happy_path.md`
- `e2e_route_subplans/06c_step_skip_blocked_assertions.md`
- `e2e_route_subplans/06d_step_skip_inspection_traceability.md`

### 07 Leaf Completion Predicates

- `e2e_route_subplans/07a_leaf_completion_route_setup.md`
- `e2e_route_subplans/07b_leaf_completion_happy_path.md`
- `e2e_route_subplans/07c_leaf_completion_blocked_assertions.md`
- `e2e_route_subplans/07d_leaf_completion_inspection_traceability.md`

### 08 Parent Merge Narrowness

- `e2e_route_subplans/08a_parent_merge_route_setup.md`
- `e2e_route_subplans/08b_parent_merge_happy_path.md`
- `e2e_route_subplans/08c_parent_merge_blocked_assertions.md`
- `e2e_route_subplans/08d_parent_merge_inspection_traceability.md`

### 09 Blocked Recovery And Resume

- `e2e_route_subplans/09a_blocked_recovery_route_setup.md`
- `e2e_route_subplans/09b_blocked_recovery_happy_path.md`
- `e2e_route_subplans/09c_blocked_recovery_blocked_assertions.md`
- `e2e_route_subplans/09d_blocked_recovery_inspection_traceability.md`

### 10 Regenerate And Recompile

- `e2e_route_subplans/10a_regenerate_recompile_route_setup.md`
- `e2e_route_subplans/10b_regenerate_recompile_happy_path.md`
- `e2e_route_subplans/10c_regenerate_recompile_blocked_assertions.md`
- `e2e_route_subplans/10d_regenerate_recompile_inspection_traceability.md`

### 11 Operator Inspection

- `e2e_route_subplans/11a_operator_inspection_route_setup.md`
- `e2e_route_subplans/11b_operator_inspection_happy_path.md`
- `e2e_route_subplans/11c_operator_inspection_blocked_assertions.md`
- `e2e_route_subplans/11d_operator_inspection_traceability.md`

### 12 Web Inspection And Bounded Actions

- `e2e_route_subplans/12a_web_route_setup.md`
- `e2e_route_subplans/12b_web_happy_path.md`
- `e2e_route_subplans/12c_web_blocked_assertions.md`
- `e2e_route_subplans/12d_web_inspection_traceability.md`

## Relationship To Parent Route Plans

These child plans decompose the route family under:

- `2026-03-12_workflow_overhaul_e2e_route_plan.md`
- `e2e_route_plans/*.md`
