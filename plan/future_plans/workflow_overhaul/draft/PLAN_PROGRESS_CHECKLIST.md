# Workflow Overhaul Draft Plan Progress Checklist

## Purpose

Track the progression of the primary workflow-overhaul draft execution queue.

Use the status vocabulary:

- `waiting`
- `in_progress`
- `blocked`
- `done`

## Primary Queue

| Name / ID | Execution Status | Blocked By | Queue Status | Notes |
| --- | --- | --- | --- | --- |
| `00` `draft_setup_plans/00_bundle_normalization_and_contract_freeze.md` | `waiting` |  | `phase_1_setup` |  |
| `01` `draft_setup_plans/01_schema_and_builtin_asset_readiness.md` | `waiting` | `00` | `phase_1_setup` |  |
| `02` `draft_setup_plans/02_runtime_surface_and_data_model_readiness.md` | `waiting` | `00`, `01` | `phase_1_setup` |  |
| `03` `draft_setup_plans/03_proving_and_traceability_readiness.md` | `waiting` | `00`, `01`, `02` | `phase_1_setup` |  |
| `04` `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md` | `waiting` | `00`, `01` | `phase_2_profile_core` |  |
| `05` `draft_feature_plans/02_profile_aware_startup_and_creation.md` | `waiting` | `00`, `02`, `04` | `phase_2_profile_core` |  |
| `06` `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md` | `waiting` | `01`, `02`, `04`, `05` | `phase_2_profile_core` |  |
| `07` `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md` | `waiting` | `01`, `02`, `04`, `05`, `06` | `phase_2_profile_core` |  |
| `08` `draft_feature_plans/05_profile_inspection_and_operator_surfaces.md` | `waiting` | `02`, `07` | `phase_2_profile_core` |  |
| `09` `draft_feature_plans/06_prompt_pack_and_prompt_selection_adoption.md` | `waiting` | `01`, `07`, `08` | `phase_2_profile_core` |  |
| `10` `draft_feature_plans/08_checklist_schema_family.md` | `waiting` | `00`, `01` | `phase_3_checklist_mode` |  |
| `11` `draft_feature_plans/09_task_profile_checklist_execution_mode_support.md` | `waiting` | `01`, `02`, `10` | `phase_3_checklist_mode` |  |
| `12` `draft_feature_plans/10_durable_checklist_persistence.md` | `waiting` | `02`, `10`, `11` | `phase_3_checklist_mode` |  |
| `13` `draft_feature_plans/11_checklist_orchestrator_loop_support.md` | `waiting` | `02`, `11`, `12` | `phase_3_checklist_mode` |  |
| `14` `draft_feature_plans/12_checklist_item_prompt_delivery.md` | `waiting` | `01`, `11`, `13` | `phase_3_checklist_mode` |  |
| `15` `draft_feature_plans/13_checklist_item_completion_and_blocker_enforcement.md` | `waiting` | `02`, `12`, `13`, `14` | `phase_3_checklist_mode` |  |
| `16` `draft_feature_plans/14_checklist_cli_and_operator_inspection.md` | `waiting` | `02`, `12`, `15` | `phase_3_checklist_mode` |  |
| `17` `draft_feature_plans/15_checklist_website_ui_support.md` | `waiting` | `02`, `12`, `15`, `16` | `phase_3_checklist_mode` |  |
| `18` `draft_feature_plans/17_workflow_profile_website_ui_support.md` | `waiting` | `02`, `05`, `07`, `08`, `09` | `phase_4_adoption` |  |
| `19` `draft_feature_plans/18_profile_and_checklist_migration_backfill.md` | `waiting` | `02`, `05`, `07`, `10`, `12` | `phase_4_adoption` |  |
| `20` `draft_feature_plans/19_workflow_profile_api_response_shapes_and_read_models.md` | `waiting` | `02`, `05`, `07`, `08` | `phase_4_adoption` |  |
| `21` `draft_feature_plans/20_workflow_profile_pydantic_models_and_contract_types.md` | `waiting` | `01`, `02`, `20` | `phase_4_adoption` |  |
| `22` `draft_feature_plans/21_workflow_profile_helper_assembly_and_compile_support.md` | `waiting` | `02`, `06`, `07`, `20`, `21` | `phase_4_adoption` |  |
| `23` `draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md` | `waiting` | `02`, `05`, `08`, `20`, `21`, `22` | `phase_4_adoption` |  |
| `24` `draft_feature_plans/23_workflow_overhaul_note_and_code_update_reconciliation.md` | `waiting` | `00`, `03`, `04`, `08`, `09` | `phase_4_adoption` |  |
| `25` `draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md` | `waiting` | `02`, `06`, `07`, `23` | `phase_4_adoption` |  |
| `26` `draft_feature_plans/25_checklist_execution_mode_rollout_and_selection_guidance.md` | `waiting` | `00`, `10`, `11` | `phase_4_adoption` |  |
| `27` `draft_feature_plans/26_checklist_flow_impact_and_relevant_flow_updates.md` | `waiting` | `03`, `13`, `16`, `26` | `phase_4_adoption` |  |
| `28` `draft_feature_plans/27_checklist_note_and_code_update_reconciliation.md` | `waiting` | `00`, `03`, `10`, `16`, `27` | `phase_4_adoption` |  |
| `29` `draft_feature_plans/28_checklist_prompt_contract_and_prompt_asset_alignment.md` | `waiting` | `01`, `14`, `17`, `26` | `phase_4_adoption` |  |
| `30` `draft_feature_plans/29_e2e_task_profile_catalog_and_route_mapping.md` | `waiting` | `01`, `03`, `04`, `05`, `20` | `phase_4_adoption` |  |
| `31` `draft_feature_plans/07_profile_e2e_and_traceability.md` | `waiting` | `03`, `04`, `05`, `06`, `07`, `08`, `09`, `18`, `20`, `21`, `22`, `23`, `24`, `30` | `phase_5_proving` |  |
| `32` `draft_feature_plans/16_checklist_e2e_and_flow_adoption.md` | `waiting` | `03`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `19`, `25`, `26`, `27`, `28`, `29` | `phase_5_proving` |  |
