# Draft Setup And Feature Plan Index

## Purpose

Index the draft setup plans and draft feature plans for the entire workflow-overhaul bundle.

This is the primary execution queue index for the `draft/` subtree.

Supporting breakdown assets such as `workflow_profile_subfeature_plans/`, `checklist_feature_plans/`, `checklist_subfeature_plans/`, `e2e_route_plans/`, and `e2e_route_subplans/` are decomposition aids, not the main execution order.

## Setup Plans

- `draft_setup_plans/00_bundle_normalization_and_contract_freeze.md`
- `draft_setup_plans/01_schema_and_builtin_asset_readiness.md`
- `draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
- `draft_setup_plans/03_proving_and_traceability_readiness.md`

## Feature Plans

Workflow-profile family:

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`
- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
- `draft_feature_plans/05_profile_inspection_and_operator_surfaces.md`
- `draft_feature_plans/06_prompt_pack_and_prompt_selection_adoption.md`
- `draft_feature_plans/07_profile_e2e_and_traceability.md`

Checklist family:

- `draft_feature_plans/08_checklist_schema_family.md`
- `draft_feature_plans/09_task_profile_checklist_execution_mode_support.md`
- `draft_feature_plans/10_durable_checklist_persistence.md`
- `draft_feature_plans/11_checklist_orchestrator_loop_support.md`
- `draft_feature_plans/12_checklist_item_prompt_delivery.md`
- `draft_feature_plans/13_checklist_item_completion_and_blocker_enforcement.md`
- `draft_feature_plans/14_checklist_cli_and_operator_inspection.md`
- `draft_feature_plans/15_checklist_website_ui_support.md`
- `draft_feature_plans/16_checklist_e2e_and_flow_adoption.md`
- `draft_feature_plans/17_workflow_profile_website_ui_support.md`
- `draft_feature_plans/18_profile_and_checklist_migration_backfill.md`
- `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md`
- `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md`
- `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md`
- `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
- `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md`
- `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
- `draft_feature_plans/25_checklist_execution_mode_rollout_and_selection_guidance.md`
- `draft_feature_plans/26_checklist_flow_impact_and_relevant_flow_updates.md`
- `draft_feature_plans/27_checklist_note_and_code_update_reconciliation.md`
- `draft_feature_plans/28_checklist_prompt_contract_and_prompt_asset_alignment.md`
- `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md`

## Sequencing

Recommended high-level order:

1. setup plans
2. workflow-profile family
3. checklist family
4. workflow-profile and checklist adoption-gap closure slices
5. E2E and flow adoption for both families

Checklist sequencing recommendation:

- do not mix checklist-mode slices into the workflow-profile core by default
- land workflow-profile core first
- then land checklist-mode runtime support
- then land the E2E/adoption layers

The main exception is a deliberate shared implementation batch where one persistence or inspection layer is being landed for both families at once.

Additional late-wave slices after the checklist runtime support:

- `draft_feature_plans/17_workflow_profile_website_ui_support.md`
- `draft_feature_plans/18_profile_and_checklist_migration_backfill.md`
- `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md`
- `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md`
- `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md`
- `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
- `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md`
- `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
- `draft_feature_plans/25_checklist_execution_mode_rollout_and_selection_guidance.md`
- `draft_feature_plans/26_checklist_flow_impact_and_relevant_flow_updates.md`
- `draft_feature_plans/27_checklist_note_and_code_update_reconciliation.md`
- `draft_feature_plans/28_checklist_prompt_contract_and_prompt_asset_alignment.md`
- `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md`

## Resolved Coverage Gap Promotions

These support-note topics are now represented by dedicated executable draft plans:

- `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md`
- `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md`
- `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md`
- `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
- `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md`
- `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
- `draft_feature_plans/25_checklist_execution_mode_rollout_and_selection_guidance.md`
- `draft_feature_plans/26_checklist_flow_impact_and_relevant_flow_updates.md`
- `draft_feature_plans/27_checklist_note_and_code_update_reconciliation.md`
- `draft_feature_plans/28_checklist_prompt_contract_and_prompt_asset_alignment.md`
- `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md`

## Support Assets That Still Remain Input-Only By Design

These future-plan assets remain support or example inputs rather than primary queue items:

- `prompts/`
- `starter_workflow_profiles/`
- `rich_layout_examples/`
- `compiled_subtask_chain_simulations/`
- `checklist_examples/`
- `checklist_future_flows/`
- `e2e_task_profiles/`

The draft queue now includes explicit feature slices for the previously missing website UI, migration/backfill, response-shape, typed-model, helper, route, gap-closure, rollout, flow-impact, prompt-alignment, and E2E-profile-catalog work.
