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

### Phase 3: Checklist Execution Mode

11. `draft_feature_plans/08_checklist_schema_family.md`
12. `draft_feature_plans/09_task_profile_checklist_execution_mode_support.md`
13. `draft_feature_plans/10_durable_checklist_persistence.md`
14. `draft_feature_plans/11_checklist_orchestrator_loop_support.md`
15. `draft_feature_plans/12_checklist_item_prompt_delivery.md`
16. `draft_feature_plans/13_checklist_item_completion_and_blocker_enforcement.md`
17. `draft_feature_plans/14_checklist_cli_and_operator_inspection.md`
18. `draft_feature_plans/15_checklist_website_ui_support.md`

### Phase 4: Proving And Adoption

19. `draft_feature_plans/17_workflow_profile_website_ui_support.md`
20. `draft_feature_plans/18_profile_and_checklist_migration_backfill.md`
21. `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md`
22. `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md`
23. `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md`
24. `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
25. `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md`
26. `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
27. `draft_feature_plans/25_checklist_execution_mode_rollout_and_selection_guidance.md`
28. `draft_feature_plans/26_checklist_flow_impact_and_relevant_flow_updates.md`
29. `draft_feature_plans/27_checklist_note_and_code_update_reconciliation.md`
30. `draft_feature_plans/28_checklist_prompt_contract_and_prompt_asset_alignment.md`
31. `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md`

### Phase 5: Proving And Adoption

32. `draft_feature_plans/07_profile_e2e_and_traceability.md`
33. `draft_feature_plans/16_checklist_e2e_and_flow_adoption.md`

## Why Checklist Work Is Not Mixed Earlier

The checklist-mode features share some schema, persistence, and inspection ideas with the workflow-profile work, but they are still a second-wave feature family.

Recommended default:

- land the workflow-profile core first
- then land checklist-mode runtime support
- then land the E2E/adoption layers for both families

Reasoning:

- the profile-aware runtime surfaces define most of the compile, materialization, blocked-action, and inspection vocabulary that checklist mode wants to reuse
- checklist mode is easier to implement cleanly once the profile-aware runtime authority and inspection surfaces are already stable
- mixing the checklist family too early would create a larger cross-system batch with more moving persistence and prompt changes at once

The main acceptable reason to mix checklist tasks into the earlier queue is if one implementation batch is intentionally landing a shared persistence or inspection layer that both families consume immediately. Otherwise, keep checklist mode as the next wave after workflow-profile core.

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

### Checklist Feature Breakdown

- `checklist_feature_plans/`
- `checklist_subfeature_plans/`

These are supporting checklist slices and should be treated as decomposition aids for:

- `draft_feature_plans/08_checklist_schema_family.md`
- `draft_feature_plans/09_task_profile_checklist_execution_mode_support.md`
- `draft_feature_plans/10_durable_checklist_persistence.md`
- `draft_feature_plans/11_checklist_orchestrator_loop_support.md`
- `draft_feature_plans/12_checklist_item_prompt_delivery.md`
- `draft_feature_plans/13_checklist_item_completion_and_blocker_enforcement.md`
- `draft_feature_plans/14_checklist_cli_and_operator_inspection.md`
- `draft_feature_plans/15_checklist_website_ui_support.md`
- `draft_feature_plans/16_checklist_e2e_and_flow_adoption.md`

Use `checklist_subfeature_plans/` when one checklist slice still needs file-per-child implementation planning.

### E2E Route Plans

- `e2e_route_plans/`
- `e2e_route_subplans/`
- `2026-03-12_workflow_overhaul_e2e_route_plan.md`

Use these to decompose:

- `draft_feature_plans/07_profile_e2e_and_traceability.md`
- `draft_feature_plans/16_checklist_e2e_and_flow_adoption.md`

Use `e2e_route_subplans/` when one route still needs setup, happy-path, blocked-path, and traceability child plans.

## Structural Rule

Inside `draft/`, the files that should be treated as executable implementation plans are:

- `draft_setup_plans/*.md`
- `draft_feature_plans/*.md`
- the top-level draft plan indexes that sequence those families

The lower-level directories exist to help spawn narrower work, not to replace the top-level queue with a 100-file flat list.
