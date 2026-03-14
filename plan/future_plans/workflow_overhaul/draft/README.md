# Workflow Overhaul Draft Plan Queue

## Purpose

This folder contains the executable draft implementation plans for the workflow-overhaul bundle.

Use this directory as the staging queue for work that may later move into the real `plan/` families.

Do not treat every file under `draft/` as part of one flat execution list. The top-level setup and feature plans are the primary queue. The subfeature and route directories are supporting breakdown assets that make those top-level plans implementable.

Progress tracking for the primary queue lives in:

- `PLAN_PROGRESS_CHECKLIST.md`

## Primary Queue

Execute these in order unless a specific implementation batch deliberately narrows scope.

### Phase 1: Setup

1. `draft_setup_plans/00_bundle_normalization_and_contract_freeze.md`
2. `draft_setup_plans/01_schema_and_builtin_asset_readiness.md`
3. `draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
4. `draft_setup_plans/03_proving_and_traceability_readiness.md`

### Phase 2: Workflow-Profile Core

5. `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
6. `draft_feature_plans/02_profile_aware_startup_and_creation.md`
7. `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
8. `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
9. `draft_feature_plans/05_profile_inspection_and_operator_surfaces.md`
10. `draft_feature_plans/06_prompt_pack_and_prompt_selection_adoption.md`

### Phase 3: Templated Task Generation

11. `draft_feature_plans/08_task_sequence_template_family.md`
12. `draft_feature_plans/09_plan_and_profile_templated_task_generation_support.md`
13. `draft_feature_plans/10_generated_task_materialization_and_dependency_freeze.md`
14. `draft_feature_plans/11_generated_task_prompt_objective_and_result_contract.md`
15. `draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`
16. `draft_feature_plans/13_generated_task_cli_and_operator_inspection.md`
17. `draft_feature_plans/14_generated_task_website_ui_support.md`

### Phase 4: Proving And Adoption

19. `draft_feature_plans/17_workflow_profile_website_ui_support.md`
20. `draft_feature_plans/18_profile_and_template_migration_backfill.md`
21. `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md`
22. `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md`
23. `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md`
24. `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
25. `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md`
26. `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
27. `draft_feature_plans/25_template_selection_and_generation_guidance.md`
28. `draft_feature_plans/26_templated_task_generation_flow_impact_and_relevant_flow_updates.md`
29. `draft_feature_plans/27_templated_task_generation_note_and_code_update_reconciliation.md`
30. `draft_feature_plans/28_template_objective_and_prompt_asset_alignment.md`
31. `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md`
32. `draft_feature_plans/30_unified_command_lifecycle_contract.md`

### Phase 5: Proving And Adoption

33. `draft_feature_plans/07_profile_e2e_and_traceability.md`
34. `draft_feature_plans/16_templated_task_generation_e2e_and_flow_adoption.md`

## Why Template Work Is Not Mixed Earlier

The template-generation features share some schema, persistence, and inspection ideas with the workflow-profile work, but they are still a second-wave feature family.

Recommended default:

- land the workflow-profile core first
- then land template-generation support
- then land the E2E/adoption layers for both families

Reasoning:

- the profile-aware runtime surfaces define most of the compile, materialization, dependency, and inspection vocabulary that template-driven generation wants to reuse
- template generation is easier to implement cleanly once the profile-aware runtime authority and inspection surfaces are already stable
- mixing the template family too early would create a larger cross-system batch with more moving persistence and prompt changes at once

The main acceptable reason to mix template-generation work into the earlier queue is if one implementation batch is intentionally landing a shared persistence or inspection layer that both families consume immediately. Otherwise, keep template generation as the next wave after workflow-profile core.

## Supporting Breakdown Assets

These are not the primary execution queue. Use them to break down a top-level draft plan into smaller follow-on tasks.

### Workflow-Profile Subfeature Plans

- `workflow_profile_subfeature_plans/`

Use these as children of:

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`
- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
- `draft_feature_plans/05_profile_inspection_and_operator_surfaces.md`
- `draft_feature_plans/07_profile_e2e_and_traceability.md`

### Template Subfeature Plans

- `template_subfeature_plans/`
- `2026-03-12_template_subfeature_plan_index.md`
- `TEMPLATE_SUBFEATURE_PROGRESS_CHECKLIST.md`

Use these as children of:

- `draft_feature_plans/08_task_sequence_template_family.md`
- `draft_feature_plans/09_plan_and_profile_templated_task_generation_support.md`
- `draft_feature_plans/10_generated_task_materialization_and_dependency_freeze.md`
- `draft_feature_plans/11_generated_task_prompt_objective_and_result_contract.md`
- `draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`
- `draft_feature_plans/13_generated_task_cli_and_operator_inspection.md`
- `draft_feature_plans/14_generated_task_website_ui_support.md`
- `draft_feature_plans/16_templated_task_generation_e2e_and_flow_adoption.md`

### Command Subfeature Plans

- `command_subfeature_plans/`
- `2026-03-13_command_subfeature_plan_index.md`

This family includes both shared command-lifecycle foundation plans and one child plan per built-in subtask command kind.

The foundation layer now explicitly includes corrective-expansion planning for verification-driven remediation and reverification loops.

Use these as children of:

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

### Template-Generation Planning Assets

Use the templated-task-generation notes and draft feature plans for reusable child-task generation:

- `../2026-03-12_templated_task_generation_overview.md`
- `../2026-03-12_task_sequence_template_schema_draft.md`
- `../2026-03-12_templated_task_generation_feature_breakdown.md`
- `draft_feature_plans/08_task_sequence_template_family.md`
- `draft_feature_plans/09_plan_and_profile_templated_task_generation_support.md`
- `draft_feature_plans/10_generated_task_materialization_and_dependency_freeze.md`
- `draft_feature_plans/11_generated_task_prompt_objective_and_result_contract.md`
- `draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`
- `draft_feature_plans/13_generated_task_cli_and_operator_inspection.md`
- `draft_feature_plans/14_generated_task_website_ui_support.md`
- `draft_feature_plans/16_templated_task_generation_e2e_and_flow_adoption.md`

### E2E Route Plans

- `e2e_route_plans/`
- `e2e_route_subplans/`
- `2026-03-12_workflow_overhaul_e2e_route_plan.md`

Use these to decompose:

- `draft_feature_plans/07_profile_e2e_and_traceability.md`
- `draft_feature_plans/16_templated_task_generation_e2e_and_flow_adoption.md`

Use `e2e_route_subplans/` when one route still needs setup, happy-path, blocked-path, and traceability child plans.

## Structural Rule

Inside `draft/`, the files that should be treated as executable implementation plans are:

- `draft_setup_plans/*.md`
- `draft_feature_plans/*.md`
- the top-level draft plan indexes that sequence those families

The lower-level directories exist to help spawn narrower work, not to replace the top-level queue with a 100-file flat list.
