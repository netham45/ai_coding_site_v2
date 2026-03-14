# Feature Checklist Backfill

## Purpose

This file is the canonical feature-status surface for the current repository.

It backfills the checklist system defined in `notes/catalogs/checklists/feature_checklist_standard.md` against the existing feature-plan set.

## Backfill Notes

- Scope basis: `plan/features/*.md`
- E2E target basis: `plan/e2e_tests/06_e2e_feature_matrix.md`
- Current real E2E assets already present in the repo: `tests/e2e/test_flow_01_create_top_level_node_real.py`, `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`, `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`, `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py`
- Interpretation rule: where the E2E matrix names a future suite that does not yet exist in `tests/e2e/`, the E2E target is still recorded here, but E2E status remains `planned`.
- Transitional documentation rule: historical entries in this backfill still use a combined `Notes` field until DU-05 migration updates each checklist entry to split `User documentation` from `Notes`.

## Feature Plan Index

Use this section for direct feature-plan-to-checklist lookup.

| Feature plan | Checklist entry |
| --- | --- |
| `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md` | `FC-01` |
| `plan/features/02_F01_configurable_node_hierarchy.md` | `FC-02` |
| `plan/features/03_F04_yaml_schema_system.md` | `FC-03` |
| `plan/features/04_F07_durable_node_lifecycle_state.md` | `FC-02` |
| `plan/features/05_F02_node_versioning_and_supersession.md` | `FC-02` |
| `plan/features/06_F27_source_document_lineage.md` | `FC-04` |
| `plan/features/07_F03_immutable_workflow_compilation.md` | `FC-05` |
| `plan/features/08_F05_default_yaml_library.md` | `FC-06` |
| `plan/features/09_F35_project_policy_extensibility.md` | `FC-04` |
| `plan/features/10_F06_override_and_merge_resolution.md` | `FC-04` |
| `plan/features/11_F08_dependency_graph_and_admission_control.md` | `FC-07` |
| `plan/features/12_F17_deterministic_branch_model.md` | `FC-08` |
| `plan/features/13_F09_node_run_orchestration.md` | `FC-09` |
| `plan/features/14_F10_ai_facing_cli_command_loop.md` | `FC-10` |
| `plan/features/15_F11_operator_cli_and_introspection.md` | `FC-11` |
| `plan/features/16_F12_session_binding_and_resume.md` | `FC-12` |
| `plan/features/17_F34_provider_agnostic_session_recovery.md` | `FC-12` |
| `plan/features/18_F13_idle_detection_and_nudge_behavior.md` | `FC-13` |
| `plan/features/19_F14_optional_pushed_child_sessions.md` | `FC-14` |
| `plan/features/20_F15_child_node_spawning.md` | `FC-07` |
| `plan/features/21_F16_manual_tree_construction.md` | `FC-07` |
| `plan/features/22_F20_conflict_detection_and_resolution.md` | `FC-08` |
| `plan/features/23_F18_child_merge_and_reconcile_pipeline.md` | `FC-08` |
| `plan/features/24_F19_regeneration_and_upstream_rectification.md` | `FC-15` |
| `plan/features/25_F21_validation_framework.md` | `FC-16` |
| `plan/features/26_F22_review_framework.md` | `FC-16` |
| `plan/features/27_F26_hook_system.md` | `FC-16` |
| `plan/features/28_F23_testing_framework_integration.md` | `FC-16` |
| `plan/features/29_F24_user_gating_and_pause_flags.md` | `FC-17` |
| `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md` | `FC-17` |
| `plan/features/31_F28_prompt_history_and_summary_history.md` | `FC-18` |
| `plan/features/32_F30_code_provenance_and_rationale_mapping.md` | `FC-19` |
| `plan/features/33_F29_documentation_generation.md` | `FC-19` |
| `plan/features/34_F32_automation_of_all_user_visible_actions.md` | `FC-20` |
| `plan/features/35_F36_auditable_history_and_reproducibility.md` | `FC-19` |
| `plan/features/36_F33_optional_isolated_runtime_environments.md` | `FC-14` |
| `plan/features/37_F10_top_level_workflow_creation_commands.md` | `FC-10` |
| `plan/features/38_F10_stage_context_retrieval_and_startup_context.md` | `FC-10` |
| `plan/features/39_F12_tmux_session_manager.md` | `FC-12` |
| `plan/features/40_F13_idle_screen_polling_and_classifier.md` | `FC-13` |
| `plan/features/41_F03_variable_substitution_and_context_rendering.md` | `FC-05` |
| `plan/features/42_F05_subtask_library_authoring.md` | `FC-06` |
| `plan/features/43_F05_prompt_pack_authoring.md` | `FC-06` |
| `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md` | `FC-03` |
| `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md` | `FC-03` |
| `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md` | `FC-10` |
| `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md` | `FC-10` |
| `plan/features/48_F11_operator_structure_and_state_commands.md` | `FC-11` |
| `plan/features/49_F11_operator_history_and_artifact_commands.md` | `FC-11` |
| `plan/features/50_F12_session_attach_resume_and_control_commands.md` | `FC-12` |
| `plan/features/51_F03_source_discovery_and_loading_pipeline.md` | `FC-05` |
| `plan/features/52_F03_schema_validation_compile_stage.md` | `FC-05` |
| `plan/features/53_F03_override_resolution_compile_stage.md` | `FC-05` |
| `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md` | `FC-05` |
| `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md` | `FC-05` |
| `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md` | `FC-05` |
| `plan/features/57_F31_database_runtime_state_schema_family.md` | `FC-01` |
| `plan/features/58_F31_database_session_attempt_history_schema_family.md` | `FC-01` |
| `plan/features/59_F30_database_provenance_docs_audit_schema_family.md` | `FC-19` |
| `plan/features/60_F05_builtin_node_task_layout_library_authoring.md` | `FC-06` |
| `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md` | `FC-06` |
| `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md` | `FC-06` |
| `plan/features/63_F03_candidate_and_rebuild_compile_variants.md` | `FC-05` |
| `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md` | `FC-07` |
| `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md` | `FC-07` |
| `plan/features/66_F05_execution_orchestration_and_result_capture.md` | `FC-09` |
| `plan/features/67_F12_provider_specific_session_recovery_surface.md` | `FC-12` |
| `plan/features/68_F25_failure_taxonomy_and_parent_decision_matrix.md` | `FC-17` |
| `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md` | `FC-16` |
| `plan/features/70_F19_live_rebuild_cutover_coordination.md` | `FC-15` |
| `plan/features/71_F11_live_git_merge_and_finalize_execution.md` | `FC-08` |
| `plan/features/72_F13_expanded_human_intervention_matrix.md` | `FC-13` |
| `plan/features/73_F30_multilanguage_provenance_expansion.md` | `FC-19` |
| `plan/features/74_F08_F18_incremental_parent_merge_overview.md` | `FC-08` |
| `plan/features/75_F08_F18_incremental_parent_merge_phase_01_durable_merge_lane_scaffolding.md` | `FC-08` |
| `plan/features/76_F18_incremental_parent_merge_phase_02_one_child_incremental_merge_execution.md` | `FC-08` |
| `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md` | `FC-07` |
| `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md` | `FC-07` |
| `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md` | `FC-09` |
| `plan/features/80_F20_incremental_parent_merge_phase_06_conflict_handoff_and_prompt_context.md` | `FC-08` |
| `plan/features/81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md` | `FC-08` |
| `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md` | `FC-08` |
| `plan/features/83_F19_dependency_aware_regeneration_scope.md` | `FC-15` |
| `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md` | `FC-15` |
| `plan/features/85_F19_version_consistent_live_runtime_authority.md` | `FC-15` |

## Checklist Entries

## FC-01: Core Daemon Authority And Runtime State

- Included feature plans: `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`, `plan/features/57_F31_database_runtime_state_schema_family.md`, `plan/features/58_F31_database_session_attempt_history_schema_family.md`
- Affected systems: Database, CLI, Daemon, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `not_applicable`; Prompts `not_applicable`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_core_orchestration_runtime.py`, `tests/e2e/test_e2e_audit_and_reproducibility_real.py`, `tests/e2e/test_e2e_session_binding_and_resume_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: Runtime-state and session-history code paths exist, but the broader named daemon/runtime E2E suites are not yet present in `tests/e2e/`.

## FC-02: Hierarchy, Lifecycle, And Versioning

- Included feature plans: `plan/features/02_F01_configurable_node_hierarchy.md`, `plan/features/04_F07_durable_node_lifecycle_state.md`, `plan/features/05_F02_node_versioning_and_supersession.md`
- Affected systems: Database, CLI, Daemon, YAML, Notes
- Status: Database `implemented`; CLI `partial`; Daemon `implemented`; YAML `implemented`; Prompts `partial`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_core_orchestration_runtime.py`, `tests/e2e/test_flow_01_create_top_level_node_real.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: Early real flow coverage exists for top-level creation, and a new full-tree skeleton now exercises real descent from epic toward tasks, but durable lifecycle, supersession, and post-merge hierarchy narratives still lack passing broader real-runtime suites.

## FC-03: YAML Schema Families

- Included feature plans: `plan/features/03_F04_yaml_schema_system.md`, `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`, `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- Affected systems: CLI, Daemon, YAML, Prompts, Notes
- Status: Database `not_applicable`; CLI `partial`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`, `tests/e2e/test_e2e_quality_chain_real.py`, `tests/e2e/test_e2e_prompt_and_summary_history_real.py`; E2E status `planned`; Performance/resilience `planned`; Overall `implemented`.
- Known limitations: Schema assets and bounded schema tests exist, but the matrix still points to future real compile and quality suites that are not yet checked in.

## FC-04: Source Lineage, Policies, And Overrides

- Included feature plans: `plan/features/06_F27_source_document_lineage.md`, `plan/features/09_F35_project_policy_extensibility.md`, `plan/features/10_F06_override_and_merge_resolution.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `partial`; Daemon `implemented`; YAML `implemented`; Prompts `partial`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`, `tests/e2e/test_e2e_provenance_and_docs_real.py`; E2E status `planned`; Performance/resilience `planned`; Overall `partial`.
- Known limitations: Override and lineage handling are covered by code and bounded tests, but the target real compile/provenance suites are still planned rather than present. The automated full-tree `cat` narrative now explicitly depends on a scoped parent decomposition selection path, and that scoping rule is planned in `notes/planning/implementation/automated_full_tree_cat_runtime_preimplementation_note.md` rather than implemented.

## FC-05: Compile Pipeline And Diagnostics

- Included feature plans: `plan/features/07_F03_immutable_workflow_compilation.md`, `plan/features/41_F03_variable_substitution_and_context_rendering.md`, `plan/features/51_F03_source_discovery_and_loading_pipeline.md`, `plan/features/52_F03_schema_validation_compile_stage.md`, `plan/features/53_F03_override_resolution_compile_stage.md`, `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`, `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`, `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`, `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`, `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`; E2E status `partial`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: The repository includes a real compile/recompile flow suite, but the fuller compile-variant and diagnostic E2E suite named in the matrix has not been added yet.

## FC-06: Default YAML, Prompt, And Built-In Library Assets

- Included feature plans: `plan/features/08_F05_default_yaml_library.md`, `plan/features/42_F05_subtask_library_authoring.md`, `plan/features/43_F05_prompt_pack_authoring.md`, `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`, `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`, `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- Affected systems: Daemon, YAML, Prompts, Notes
- Status: Database `not_applicable`; CLI `not_applicable`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`, `tests/e2e/test_e2e_quality_chain_real.py`, `tests/e2e/test_e2e_prompt_and_summary_history_real.py`; E2E status `planned`; Performance/resilience `not_applicable`; Overall `implemented`.
- Known limitations: Built-in assets are present and exercised indirectly by bounded tests, but the target real suites for built-in selection and prompt delivery are still future work.

## FC-07: Dependencies, Child Materialization, And Tree Editing

- Included feature plans: `plan/features/11_F08_dependency_graph_and_admission_control.md`, `plan/features/20_F15_child_node_spawning.md`, `plan/features/21_F16_manual_tree_construction.md`, `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`, `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`, `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`, `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- Affected systems: Database, CLI, Daemon, YAML, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `implemented`; Prompts `not_applicable`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`, `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py`, `tests/e2e/test_e2e_dependency_and_child_materialization_real.py`, `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`, `tests/e2e/test_e2e_incremental_parent_merge_real.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: The repo has real flow coverage for materialization and manual tree edits, and the new incremental parent-merge E2E now proves merge-backed sibling dependency unblock plus stale-child refresh on the happy path. Richer blocker explanation, hybrid reconciliation, conflict/restart hardening, and the full hierarchical merge story still rely on planned or expected-failing suites. For the automated full-tree `cat` narrative specifically, parent-driven generated-layout authority and daemon-owned automatic child start are still planned rather than implemented.

## FC-08: Branching, Conflicts, And Live Mergeback

- Included feature plans: `plan/features/12_F17_deterministic_branch_model.md`, `plan/features/22_F20_conflict_detection_and_resolution.md`, `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`, `plan/features/71_F11_live_git_merge_and_finalize_execution.md`, `plan/features/74_F08_F18_incremental_parent_merge_overview.md`, `plan/features/75_F08_F18_incremental_parent_merge_phase_01_durable_merge_lane_scaffolding.md`, `plan/features/76_F18_incremental_parent_merge_phase_02_one_child_incremental_merge_execution.md`, `plan/features/80_F20_incremental_parent_merge_phase_06_conflict_handoff_and_prompt_context.md`, `plan/features/81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md`, `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`
- Affected systems: Database, CLI, Daemon, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `not_applicable`; Prompts `partial`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_branch_identity_and_history_real.py`, `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`, `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`, `tests/e2e/test_e2e_incremental_parent_merge_real.py`, `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: Git-oriented code and bounded tests exist, and the repo now has real E2E proof for the live bootstrap/merge/finalize/status path, hierarchy-wide rollback/reset through the real `node rectify-upstream` path, plus real incremental parent-merge E2E coverage for happy-path sibling unblock, stale-child refresh, conflict handoff/resolution on the existing intervention surface, restart-safe merge-lane resumption after daemon interruption, post-merge parent reconcile inspection, and hierarchy-wide task -> plan -> phase -> epic propagation through the daemon-owned incremental merge lane. Resolved-output content after conflicted merge reconciliation and workspace-root repo placement still remain open limitations.

## FC-09: Node Run Orchestration And Result Capture

- Included feature plans: `plan/features/13_F09_node_run_orchestration.md`, `plan/features/66_F05_execution_orchestration_and_result_capture.md`, `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `implemented`; Prompts `partial`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`, `tests/e2e/test_e2e_incremental_parent_merge_real.py`, `tests/e2e/test_e2e_core_orchestration_runtime.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: The repo now has a real Flow 05 checkpoint for the shipped durable run-control loop, and the incremental parent-merge E2E family now proves the daemon background loop can advance a happy-path incremental merge, refresh the dependent child onto the merged parent head, auto-start that child before parent reconcile inspection, and propagate finalized no-run hierarchy changes upward through task -> plan -> phase -> epic. The broader core-orchestration runtime suite is still incomplete, and for the automated full-tree `cat` narrative specifically, multi-tier parent decomposition remains planned rather than implemented.

## FC-10: AI CLI Runtime Surface

- Included feature plans: `plan/features/14_F10_ai_facing_cli_command_loop.md`, `plan/features/37_F10_top_level_workflow_creation_commands.md`, `plan/features/38_F10_stage_context_retrieval_and_startup_context.md`, `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`, `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- Affected systems: Database, CLI, Daemon, Prompts, Notes
- Status: Database `partial`; CLI `implemented`; Daemon `implemented`; YAML `not_applicable`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_flow_01_create_top_level_node_real.py`, `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`, `tests/e2e/test_e2e_operator_cli_surface.py`, `tests/e2e/test_e2e_core_orchestration_runtime.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: The repo now has real checkpoints for top-level startup, the startup path auto-binds a primary session when `start_run` is requested, and the shipped durable command loop plus full-tree skeleton exercise more of the CLI path across hierarchy depth. Most broader AI-facing CLI narratives still point to future operator/runtime suites, and startup is still not fully atomic if session launch fails after run admission.

## FC-11: Operator CLI Introspection Surface

- Included feature plans: `plan/features/15_F11_operator_cli_and_introspection.md`, `plan/features/48_F11_operator_structure_and_state_commands.md`, `plan/features/49_F11_operator_history_and_artifact_commands.md`
- Affected systems: Database, CLI, Daemon, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `not_applicable`; Prompts `not_applicable`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_operator_cli_surface.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Operator-facing CLI coverage is strong at bounded layers, and the new full-tree skeleton now proves some multi-level inspection surfaces, but the dedicated real CLI surface suite named in the matrix still does not exist.

## FC-12: Session Lifecycle And Recovery

- Included feature plans: `plan/features/16_F12_session_binding_and_resume.md`, `plan/features/17_F34_provider_agnostic_session_recovery.md`, `plan/features/39_F12_tmux_session_manager.md`, `plan/features/50_F12_session_attach_resume_and_control_commands.md`, `plan/features/67_F12_provider_specific_session_recovery_surface.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `partial`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_session_binding_and_resume_real.py`, `tests/e2e/test_e2e_tmux_session_runtime_real.py`, `tests/e2e/test_e2e_provider_recovery_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Session binding and resume foundations are implemented, including Codex-backed primary-session bind and recovery launch plans, and the daemon now autonomously supervises tracked active tmux sessions with passing real tmux proof for killed-session replacement. The remaining gap is the stronger real tmux E2E for the unrecoverable replacement-failure branch; that failure path is currently proved at bounded layers rather than with a stable passing live-tmux scenario.

## FC-13: Idle Detection And Human Intervention Expansion

- Included feature plans: `plan/features/18_F13_idle_detection_and_nudge_behavior.md`, `plan/features/40_F13_idle_screen_polling_and_classifier.md`, `plan/features/72_F13_expanded_human_intervention_matrix.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `partial`; CLI `partial`; Daemon `partial`; YAML `partial`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_tmux_session_runtime_real.py`, `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: The repo contains idle and intervention code paths plus bounded coverage, but dedicated real tmux/Codex idle, nudge, repeated-idle, and live session-originated completion/failure E2E suites are still future work, and the first prompt-bootstrap E2E currently shows the primary session may exit before the expected prompt log is written.

## FC-14: Child Session Isolation And Optional Runtime Environments

- Included feature plans: `plan/features/19_F14_optional_pushed_child_sessions.md`, `plan/features/36_F33_optional_isolated_runtime_environments.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `partial`; CLI `partial`; Daemon `partial`; YAML `partial`; Prompts `implemented`; Notes `implemented`; Bounded tests `partial`; E2E target `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`, `tests/e2e/test_e2e_session_binding_and_resume_real.py`; E2E status `planned`; Performance/resilience `planned`; Overall `partial`.
- Known limitations: Child-session behavior is partially implemented, and optional isolated environments remain intentionally deferred beyond the first implementation path.

## FC-15: Regeneration And Live Cutover

- Included feature plans: `plan/features/24_F19_regeneration_and_upstream_rectification.md`, `plan/features/70_F19_live_rebuild_cutover_coordination.md`, `plan/features/83_F19_dependency_aware_regeneration_scope.md`, `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`, `plan/features/85_F19_version_consistent_live_runtime_authority.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `partial`; Daemon `partial`; YAML `implemented`; Prompts `partial`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`, `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`, `tests/e2e/test_e2e_incremental_parent_merge_real.py`, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`; E2E status `partial`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: Regeneration logic and bounded proof exist, and rebuild history plus cutover-readiness now expose explicit replay classification, replay-incomplete blocking, stale-baseline blocking, required cutover-scope enumeration, grouped scope readiness, and the narrow `ready_with_follow_on_replay` ancestor-cutover status for dependency-invalidated fresh-restart descendants. The dedicated live blocker suite `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` now proves real upstream rectification blocking on active authoritative runs and real candidate cutover blocking on active authoritative tmux primary sessions. The dedicated rectification suite `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py` now proves the base subtree-regenerate/upstream-rectify round trip and dependency-invalidated sibling remap into rebuilt parent candidates. `tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k rectify` now proves the hierarchy-wide rollback/reset narrative through a second authoritative task revision, upstream candidate rebuild, stale-content reset, and grouped ancestor cutover. Real Flow 10 still carries the grouped-cutover checkpoint where a rebuilt parent cutover carries its rebuilt child scope with it, and `tests/e2e/test_e2e_incremental_parent_merge_real.py` proves all three real post-cutover follow-on branches that currently exist: layout-authoritative dependents rematerialize a fresh layout-owned child tree, prior-manual dependents can clear the rebuild gate through real `preserve_manual` reconciliation on the fresh version, and prior-manual dependents can also clear that gate by creating a new manual child on the fresh version. The feature remains partial because CLI, daemon, prompt, and resilience scope outside those proved narratives is still broader than the passing E2E set.

## FC-16: Quality Gates And Hooked Finalization

- Included feature plans: `plan/features/25_F21_validation_framework.md`, `plan/features/26_F22_review_framework.md`, `plan/features/27_F26_hook_system.md`, `plan/features/28_F23_testing_framework_integration.md`, `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `partial`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_quality_chain_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Validation, review, testing, and hook code is present with bounded coverage, but the end-to-end quality-chain suite is still a target rather than a checked-in test.

## FC-17: User Gating And Failure Decision Logic

- Included feature plans: `plan/features/29_F24_user_gating_and_pause_flags.md`, `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`, `plan/features/68_F25_failure_taxonomy_and_parent_decision_matrix.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Failure and pause handling are implemented at code and bounded-test layers, but the full real escalation/intervention narrative is still pending.

## FC-18: Prompt And Summary History

- Included feature plans: `plan/features/31_F28_prompt_history_and_summary_history.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `implemented`; Prompts `implemented`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_prompt_and_summary_history_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Prompt-history and summary-history persistence appear implemented, but the dedicated real audit suite is still planned.

## FC-19: Provenance, Documentation, And Audit Surfaces

- Included feature plans: `plan/features/32_F30_code_provenance_and_rationale_mapping.md`, `plan/features/33_F29_documentation_generation.md`, `plan/features/35_F36_auditable_history_and_reproducibility.md`, `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`, `plan/features/73_F30_multilanguage_provenance_expansion.md`
- Affected systems: Database, CLI, Daemon, YAML, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `partial`; Prompts `not_applicable`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/test_e2e_provenance_and_docs_real.py`, `tests/e2e/test_e2e_audit_and_reproducibility_real.py`, `tests/e2e/test_e2e_branch_identity_and_history_real.py`; E2E status `planned`; Performance/resilience `partial`; Overall `partial`.
- Known limitations: Provenance, docs, and audit code paths exist, but real multi-language provenance and audit reconstruction suites are still future work.

## FC-20: Automation Coverage Of User-Visible Actions

- Included feature plans: `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `partial`; CLI `partial`; Daemon `partial`; YAML `partial`; Prompts `partial`; Notes `implemented`; Bounded tests `partial`; E2E target `tests/e2e/test_e2e_operator_cli_surface.py`, `tests/e2e/test_e2e_core_orchestration_runtime.py`; E2E status `planned`; Performance/resilience `planned`; Overall `partial`.
- Known limitations: The repo has many automatable paths, but there is not yet a single enforced checklist proving that every user-visible action has a complete automated route and real runtime proof.
