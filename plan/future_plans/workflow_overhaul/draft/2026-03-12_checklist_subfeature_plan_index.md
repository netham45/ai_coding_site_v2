# Checklist Subfeature Plan Index

## Purpose

Provide a deeper implementation-sized breakdown for the checklist execution-mode family where the checklist feature slices are still too coarse.

## Structure

The checklist family now uses file-per-child plans under `checklist_subfeature_plans/`.

## Families

### A Checklist Schema Family

- `checklist_subfeature_plans/A1_schema_definition_model.md`
- `checklist_subfeature_plans/A2_template_definition_model.md`
- `checklist_subfeature_plans/A3_instance_definition_model.md`
- `checklist_subfeature_plans/A4_status_and_blocker_vocabulary.md`
- `checklist_subfeature_plans/A5_validation_and_document_proof.md`

### B Task/Profile Execution-Mode Support

- `checklist_subfeature_plans/B1_profile_execution_mode_fields.md`
- `checklist_subfeature_plans/B2_compile_context_checklist_freeze.md`
- `checklist_subfeature_plans/B3_selection_and_activation_rules.md`
- `checklist_subfeature_plans/B4_instance_attachment_contract.md`
- `checklist_subfeature_plans/B5_startup_and_transition_posture.md`

### C Durable Checklist Persistence

- `checklist_subfeature_plans/C1_instance_storage_model.md`
- `checklist_subfeature_plans/C2_item_transition_persistence.md`
- `checklist_subfeature_plans/C3_blocker_and_unblock_storage.md`
- `checklist_subfeature_plans/C4_history_and_restart_reconstruction.md`
- `checklist_subfeature_plans/C5_migration_and_backfill_posture.md`

### D Orchestrator Loop Support

- `checklist_subfeature_plans/D1_next_legal_item_selection.md`
- `checklist_subfeature_plans/D2_dependency_and_readiness_evaluation.md`
- `checklist_subfeature_plans/D3_single_active_item_invariant.md`
- `checklist_subfeature_plans/D4_terminal_return_handoff.md`
- `checklist_subfeature_plans/D5_blocked_and_not_applicable_reevaluation.md`

### E Checklist Item Prompt Delivery

- `checklist_subfeature_plans/E1_prompt_asset_layout.md`
- `checklist_subfeature_plans/E2_context_injection_contract.md`
- `checklist_subfeature_plans/E3_allowed_options_rendering.md`
- `checklist_subfeature_plans/E4_terminal_result_schema.md`
- `checklist_subfeature_plans/E5_prompt_inspection_and_retrieval.md`

### F Item Completion And Blocker Enforcement

- `checklist_subfeature_plans/F1_completed_predicate_validation.md`
- `checklist_subfeature_plans/F2_blocked_payload_validation.md`
- `checklist_subfeature_plans/F3_not_applicable_policy.md`
- `checklist_subfeature_plans/F4_invalid_terminal_result_rejection.md`
- `checklist_subfeature_plans/F5_unblock_transition_legality.md`

### G CLI And Operator Inspection

- `checklist_subfeature_plans/G1_checklist_summary_read_model.md`
- `checklist_subfeature_plans/G2_active_item_detail_surface.md`
- `checklist_subfeature_plans/G3_cli_command_family.md`
- `checklist_subfeature_plans/G4_blocker_and_result_rendering.md`
- `checklist_subfeature_plans/G5_audit_and_history_alignment.md`

### H Website UI Support

- `checklist_subfeature_plans/H1_summary_view.md`
- `checklist_subfeature_plans/H2_active_item_detail_view.md`
- `checklist_subfeature_plans/H3_bounded_action_surface.md`
- `checklist_subfeature_plans/H4_blocker_and_not_applicable_rendering.md`
- `checklist_subfeature_plans/H5_browser_sync_and_refresh.md`

### I E2E Coverage

- `checklist_subfeature_plans/I1_active_item_execution_e2e.md`
- `checklist_subfeature_plans/I2_blocked_persistence_e2e.md`
- `checklist_subfeature_plans/I3_not_applicable_e2e.md`
- `checklist_subfeature_plans/I4_recovery_restart_e2e.md`
- `checklist_subfeature_plans/I5_inspection_parity_e2e.md`

## Relationship To Parent Checklist Slices

These child plans decompose:

- `checklist_feature_plans/A_checklist_schema_family.md`
- `checklist_feature_plans/B_task_profile_execution_mode_support.md`
- `checklist_feature_plans/C_durable_checklist_persistence.md`
- `checklist_feature_plans/D_orchestrator_loop_support.md`
- `checklist_feature_plans/E_checklist_item_prompt_delivery.md`
- `checklist_feature_plans/F_item_completion_and_blocker_enforcement.md`
- `checklist_feature_plans/G_cli_and_operator_inspection.md`
- `checklist_feature_plans/H_website_ui_support.md`
- `checklist_feature_plans/I_e2e_coverage.md`
