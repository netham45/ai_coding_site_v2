# Workflow Profile Subfeature Plan Index

## Purpose

Provide a deeper implementation-sized breakdown for the workflow-profile family where the broader draft feature plans are still too coarse.

## Structure

The directory now uses 50 standalone child-plan files instead of 10 grouped parent files.

## Families

### 01 Schema Family Adoption

- `workflow_profile_subfeature_plans/01a_model_definition.md`
- `workflow_profile_subfeature_plans/01b_family_registration.md`
- `workflow_profile_subfeature_plans/01c_builtin_asset_layout.md`
- `workflow_profile_subfeature_plans/01d_cross_reference_validation.md`
- `workflow_profile_subfeature_plans/01e_document_and_schema_proof.md`

### 02 Node-Definition Extension

- `workflow_profile_subfeature_plans/02a_default_and_supported_profile_fields.md`
- `workflow_profile_subfeature_plans/02b_hierarchy_loader_support.md`
- `workflow_profile_subfeature_plans/02c_builtin_node_asset_updates.md`
- `workflow_profile_subfeature_plans/02d_validation_rules.md`
- `workflow_profile_subfeature_plans/02e_downstream_runtime_consumers.md`

### 03 Layout-Definition Extension

- `workflow_profile_subfeature_plans/03a_top_level_layout_profile_metadata.md`
- `workflow_profile_subfeature_plans/03b_child_role_and_profile_metadata.md`
- `workflow_profile_subfeature_plans/03c_compatibility_validation.md`
- `workflow_profile_subfeature_plans/03d_generated_layout_contract.md`
- `workflow_profile_subfeature_plans/03e_materialization_facing_projection.md`

### 04 Startup Request And Profile Persistence

- `workflow_profile_subfeature_plans/04a_request_response_model_extension.md`
- `workflow_profile_subfeature_plans/04b_cli_flag_wiring.md`
- `workflow_profile_subfeature_plans/04c_version_persistence.md`
- `workflow_profile_subfeature_plans/04d_top_level_legality_enforcement.md`
- `workflow_profile_subfeature_plans/04e_failure_and_recovery_posture.md`

### 05 Materialization Layout Resolution

- `workflow_profile_subfeature_plans/05a_default_layout_resolution.md`
- `workflow_profile_subfeature_plans/05b_explicit_override_resolution.md`
- `workflow_profile_subfeature_plans/05c_generated_layout_precedence.md`
- `workflow_profile_subfeature_plans/05d_runtime_response_metadata.md`
- `workflow_profile_subfeature_plans/05e_idempotency_and_replan_behavior.md`

### 06 Child-Role Enforcement

- `workflow_profile_subfeature_plans/06a_required_role_coverage_calculation.md`
- `workflow_profile_subfeature_plans/06b_missing_role_failure_classification.md`
- `workflow_profile_subfeature_plans/06c_extra_role_policy.md`
- `workflow_profile_subfeature_plans/06d_child_profile_default_mapping.md`
- `workflow_profile_subfeature_plans/06e_non_leaf_blocked_actions.md`

### 07 Compile-Context Profile Freezing

- `workflow_profile_subfeature_plans/07a_selected_profile_snapshot.md`
- `workflow_profile_subfeature_plans/07b_effective_layout_snapshot.md`
- `workflow_profile_subfeature_plans/07c_obligation_snapshot.md`
- `workflow_profile_subfeature_plans/07d_ancestry_profile_chain_snapshot.md`
- `workflow_profile_subfeature_plans/07e_compile_failure_visibility.md`

### 08 Brief Generation

- `workflow_profile_subfeature_plans/08a_brief_payload_schema.md`
- `workflow_profile_subfeature_plans/08b_prompt_stack_composition.md`
- `workflow_profile_subfeature_plans/08c_child_recommendation_projection.md`
- `workflow_profile_subfeature_plans/08d_persistence_and_retrieval.md`
- `workflow_profile_subfeature_plans/08e_failure_and_drift_rules.md`

### 09 Profile Read Surfaces

- `workflow_profile_subfeature_plans/09a_node_types.md`
- `workflow_profile_subfeature_plans/09b_node_profiles.md`
- `workflow_profile_subfeature_plans/09c_workflow_brief.md`
- `workflow_profile_subfeature_plans/09d_repo_wide_profile_catalog.md`
- `workflow_profile_subfeature_plans/09e_cli_web_consumer_alignment.md`

### 10 E2E Route Family

- `workflow_profile_subfeature_plans/10a_parentless_start_route.md`
- `workflow_profile_subfeature_plans/10b_ladder_routes.md`
- `workflow_profile_subfeature_plans/10c_enforcement_routes.md`
- `workflow_profile_subfeature_plans/10d_recovery_and_recompile_routes.md`
- `workflow_profile_subfeature_plans/10e_inspection_and_web_routes.md`

## Relationship To Broader Draft Feature Plans

These subfeature plans are the deeper children of:

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`
- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
- `draft_feature_plans/05_profile_inspection_and_operator_surfaces.md`
- `draft_feature_plans/07_profile_e2e_and_traceability.md`
