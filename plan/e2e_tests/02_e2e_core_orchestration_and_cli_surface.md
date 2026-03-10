# Phase E2E-02: E2E Core Orchestration And CLI Surface

## Goal

Create real E2E suites for the core orchestration, compile, CLI, and operator-surface features that define the main runtime control loop.

## Rationale

- Rationale: A large portion of the repository's feature inventory describes the real user and operator path for creating work, compiling workflows, inspecting state, and driving runtime mutations.
- Reason for existence: This phase exists to raise those core features from bounded proof to real-stack proof through the strongest user-visible runtime path.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/03_F04_yaml_schema_system.md`
- `plan/features/04_F07_durable_node_lifecycle_state.md`
- `plan/features/05_F02_node_versioning_and_supersession.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/08_F05_default_yaml_library.md`
- `plan/features/09_F35_project_policy_extensibility.md`
- `plan/features/10_F06_override_and_merge_resolution.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/38_F10_stage_context_retrieval_and_startup_context.md`
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/49_F11_operator_history_and_artifact_commands.md`
- `plan/features/51_F03_source_discovery_and_loading_pipeline.md`
- `plan/features/52_F03_schema_validation_compile_stage.md`
- `plan/features/53_F03_override_resolution_compile_stage.md`
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`
- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: real E2E suites must assert durable node creation, workflow compilation, lifecycle changes, versioning, compile failures, prompt history, and audit surfaces where applicable.
- CLI: use real CLI subprocess commands for create/compile/show/inspect/progress operations.
- Daemon: use real daemon startup and real API boundaries; do not use in-process daemon bridges as the strongest proof.
- YAML: prove YAML schema, policy, override, and library effects through actual compilation and runtime-visible outputs.
- Prompts: prove prompt pack selection, rendered payload freeze, and prompt/context retrieval where those features are in scope.
- Notes: record canonical commands and current support levels for the suite family.
- Tests: build E2E suites around real operator narratives rather than per-helper assertions.
- Performance: keep compile/orchestration E2E scope bounded enough for regular reruns.

## Proposed Suite Families

- `tests/e2e/test_flow_01_create_top_level_node_real.py`
- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- `tests/e2e/test_e2e_core_orchestration_runtime.py`
- `tests/e2e/test_e2e_operator_cli_surface.py`
- `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`

## Exit Criteria

- core create/compile/inspect/progress behavior is proven through real daemon plus real CLI paths
- compile-stage and YAML/prompt features are proven through actual runtime-visible compiled outputs
- operator inspection surfaces are proven through real CLI/API reads of durable state
