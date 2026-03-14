# Template Subfeature Plan Progress Checklist

## Purpose

Track the progression of the templated-task-generation subfeature-plan family.

Use the status vocabulary:

- `waiting`
- `in_progress`
- `blocked`
- `done`

## Queue

| Name / ID | Execution Status | Blocked By | Parent Area | Notes |
| --- | --- | --- | --- | --- |
| `08a` `template_subfeature_plans/08a_schema_definition_model.md` | `waiting` |  | `08_template_schema_family` |  |
| `08b` `template_subfeature_plans/08b_template_definition_model.md` | `waiting` | `08a` | `08_template_schema_family` |  |
| `08c` `template_subfeature_plans/08c_step_dependency_validation.md` | `waiting` | `08a`, `08b` | `08_template_schema_family` |  |
| `08d` `template_subfeature_plans/08d_builtin_asset_layout.md` | `waiting` | `08a`, `08b` | `08_template_schema_family` |  |
| `08e` `template_subfeature_plans/08e_document_and_schema_proof.md` | `waiting` | `08a`, `08b`, `08c`, `08d` | `08_template_schema_family` |  |
| `09a` `template_subfeature_plans/09a_plan_reference_fields.md` | `waiting` | `08b` | `09_reference_and_selection` |  |
| `09b` `template_subfeature_plans/09b_profile_reference_fields.md` | `waiting` | `08b` | `09_reference_and_selection` |  |
| `09c` `template_subfeature_plans/09c_selection_rules.md` | `waiting` | `09a`, `09b` | `09_reference_and_selection` |  |
| `09d` `template_subfeature_plans/09d_compile_time_freeze.md` | `waiting` | `09a`, `09b`, `09c` | `09_reference_and_selection` |  |
| `09e` `template_subfeature_plans/09e_startup_legality_posture.md` | `waiting` | `09a`, `09b`, `09c` | `09_reference_and_selection` |  |
| `10a` `template_subfeature_plans/10a_materialization_trigger_points.md` | `waiting` | `09c`, `09d`, `09e` | `10_materialization` |  |
| `10b` `template_subfeature_plans/10b_step_to_task_lineage.md` | `waiting` | `10a` | `10_materialization` |  |
| `10c` `template_subfeature_plans/10c_dependency_edge_freeze.md` | `waiting` | `10a`, `10b` | `10_materialization` |  |
| `10d` `template_subfeature_plans/10d_idempotent_rematerialization.md` | `waiting` | `10a`, `10b`, `10c` | `10_materialization` |  |
| `10e` `template_subfeature_plans/10e_replacement_version_behavior.md` | `waiting` | `10a`, `10b`, `10c`, `10d` | `10_materialization` |  |
| `11a` `template_subfeature_plans/11a_template_context_payload.md` | `waiting` | `09d`, `10b` | `11_objective_propagation` |  |
| `11b` `template_subfeature_plans/11b_prompt_injection_contract.md` | `waiting` | `11a` | `11_objective_propagation` |  |
| `11c` `template_subfeature_plans/11c_expected_output_projection.md` | `waiting` | `11a` | `11_objective_propagation` |  |
| `11d` `template_subfeature_plans/11d_proving_target_projection.md` | `waiting` | `11a` | `11_objective_propagation` |  |
| `11e` `template_subfeature_plans/11e_result_contract_alignment.md` | `waiting` | `11a`, `11b`, `11c`, `11d` | `11_objective_propagation` |  |
| `12a` `template_subfeature_plans/12a_completion_validation.md` | `waiting` | `10c`, `11e` | `12_completion_and_drift` |  |
| `12b` `template_subfeature_plans/12b_blocker_and_dependency_readiness.md` | `waiting` | `10c`, `12a` | `12_completion_and_drift` |  |
| `12c` `template_subfeature_plans/12c_retry_and_resume_posture.md` | `waiting` | `10d`, `10e`, `12a`, `12b` | `12_completion_and_drift` |  |
| `12d` `template_subfeature_plans/12d_recompile_drift_classification.md` | `waiting` | `10e`, `12a`, `12c` | `12_completion_and_drift` |  |
| `12e` `template_subfeature_plans/12e_reconciliation_rules.md` | `waiting` | `12b`, `12c`, `12d` | `12_completion_and_drift` |  |
| `13a` `template_subfeature_plans/13a_read_model_shape.md` | `waiting` | `10b`, `12b` | `13_inspection_surfaces` |  |
| `13b` `template_subfeature_plans/13b_cli_rendering.md` | `waiting` | `13a` | `13_inspection_surfaces` |  |
| `13c` `template_subfeature_plans/13c_authored_vs_generated_visibility.md` | `waiting` | `13a`, `13b` | `13_inspection_surfaces` |  |
| `13d` `template_subfeature_plans/13d_history_and_audit_alignment.md` | `waiting` | `10b`, `12d`, `13a` | `13_inspection_surfaces` |  |
| `13e` `template_subfeature_plans/13e_operator_consumer_alignment.md` | `waiting` | `13a`, `13b`, `13c`, `13d` | `13_inspection_surfaces` |  |
| `14a` `template_subfeature_plans/14a_generated_child_grouping.md` | `waiting` | `13a`, `13c` | `14_website_ui` |  |
| `14b` `template_subfeature_plans/14b_template_provenance_detail.md` | `waiting` | `13a`, `13e` | `14_website_ui` |  |
| `14c` `template_subfeature_plans/14c_dependency_rendering.md` | `waiting` | `12b`, `13a`, `14a` | `14_website_ui` |  |
| `14d` `template_subfeature_plans/14d_bounded_action_alignment.md` | `waiting` | `12b`, `13e`, `14c` | `14_website_ui` |  |
| `14e` `template_subfeature_plans/14e_browser_refresh_and_sync.md` | `waiting` | `13e`, `14a`, `14b`, `14c`, `14d` | `14_website_ui` |  |
| `16a` `template_subfeature_plans/16a_materialization_route_setup.md` | `waiting` | `10a`, `10b`, `12b` | `16_e2e_and_flow_adoption` |  |
| `16b` `template_subfeature_plans/16b_generated_child_execution_happy_path.md` | `waiting` | `16a` | `16_e2e_and_flow_adoption` |  |
| `16c` `template_subfeature_plans/16c_generated_child_blocked_assertions.md` | `waiting` | `12b`, `16a`, `16b` | `16_e2e_and_flow_adoption` |  |
| `16d` `template_subfeature_plans/16d_provenance_inspection_traceability.md` | `waiting` | `13e`, `14b`, `16b` | `16_e2e_and_flow_adoption` |  |
| `16e` `template_subfeature_plans/16e_recompile_and_recovery_routes.md` | `waiting` | `12c`, `12d`, `12e`, `16b`, `16c`, `16d` | `16_e2e_and_flow_adoption` |  |

## Parent Mapping

- `08a` through `08e` support `draft_feature_plans/08_task_sequence_template_family.md`
- `09a` through `09e` support `draft_feature_plans/09_plan_and_profile_templated_task_generation_support.md`
- `10a` through `10e` support `draft_feature_plans/10_generated_task_materialization_and_dependency_freeze.md`
- `11a` through `11e` support `draft_feature_plans/11_generated_task_prompt_objective_and_result_contract.md`
- `12a` through `12e` support `draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`
- `13a` through `13e` support `draft_feature_plans/13_generated_task_cli_and_operator_inspection.md`
- `14a` through `14e` support `draft_feature_plans/14_generated_task_website_ui_support.md`
- `16a` through `16e` support `draft_feature_plans/16_templated_task_generation_e2e_and_flow_adoption.md`
