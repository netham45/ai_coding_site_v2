# Phase E2E-06: Feature-To-Suite Matrix

## Goal

Map every existing feature plan to at least one real-code E2E suite target.

## Rationale

- Rationale: The E2E effort only becomes enforceable if every feature has an explicit real-code target instead of relying on broad statements that “the suite will eventually cover it”.
- Reason for existence: This phase exists to prevent silent omissions and to make future E2E progress auditable feature by feature.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`

## Required Notes

- `AGENTS.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

Interpretation rule:

- this matrix assigns real-E2E targets only
- it does not claim that the named suite already exists or is already passing
- current real-E2E completion state lives in `notes/catalogs/checklists/feature_checklist_backfill.md` and `notes/catalogs/audit/flow_coverage_checklist.md`

## Scope

- Database: map DB-backed feature families to at least one real persistence and inspection suite target.
- CLI: map CLI-facing features to real CLI subprocess or operator-surface suite targets where applicable.
- Daemon: map daemon-owned runtime features to real daemon subprocess and API-boundary suites.
- YAML: map compile and declarative-runtime features to real compile/runtime suite targets rather than schema-only proof.
- Prompts: map prompt-linked runtime features to suites that exercise real prompt selection, delivery, or history behavior where applicable.
- Notes: keep feature-to-suite target assignment explicit and auditable without overstating completion.
- Tests: define explicit real-E2E target coverage, not bounded or simulated substitutes.
- Performance: keep the matrix usable as a traceability surface rather than a duplicate of performance policy docs.

## Matrix

### Core orchestration, compile, YAML, and operator surfaces

- `01_F31_daemon_authority_and_durable_orchestration_record.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real daemon authority mutations, durable state reads, operator inspection.
- `02_F01_configurable_node_hierarchy.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: create legal and illegal real nodes through CLI/API, and prove one full hierarchy descent through real durable state.
- `03_F04_yaml_schema_system.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: validate real YAML assets through real CLI/API and compile paths.
- `04_F07_durable_node_lifecycle_state.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real lifecycle transitions, durable reads, resume-safe cursor behavior.
- `05_F02_node_versioning_and_supersession.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real node version creation, supersession, and authoritative-version inspection.
- `07_F03_immutable_workflow_compilation.md` -> `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`: real compile and recompile against the daemon/CLI path.
- `08_F05_default_yaml_library.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: compile real built-in node kinds through shipped YAML.
- `09_F35_project_policy_extensibility.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: apply real project policy overrides in an isolated workspace and verify compiled effects.
- `10_F06_override_and_merge_resolution.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real override docs, compile results, and failure diagnostics.
- `13_F09_node_run_orchestration.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real node-run start/advance/complete/fail path with durable run state, including the leaf-task stage inside a hierarchy narrative.
- `14_F10_ai_facing_cli_command_loop.md` -> `tests/e2e/test_e2e_operator_cli_surface.py`: real AI-facing CLI command loop against the daemon subprocess.
- `15_F11_operator_cli_and_introspection.md` -> `tests/e2e/test_e2e_operator_cli_surface.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real structure/state/history reads through the operator CLI, including one multi-level tree narrative.
- `37_F10_top_level_workflow_creation_commands.md` -> `tests/e2e/test_flow_01_create_top_level_node_real.py`: real prompt-driven top-level workflow creation.
- `38_F10_stage_context_retrieval_and_startup_context.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real prompt/context retrieval for the current subtask.
- `41_F03_variable_substitution_and_context_rendering.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real rendered payload freeze from YAML and prompt assets.
- `46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md` -> `tests/e2e/test_e2e_operator_cli_surface.py`: real work-retrieval commands from a live run.
- `47_F10_ai_cli_progress_and_stage_transition_commands.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real progress, heartbeat, complete, fail, and advance commands.
- `48_F11_operator_structure_and_state_commands.md` -> `tests/e2e/test_e2e_operator_cli_surface.py`: real tree, blockers, current task/subtask, and node state inspection.
- `49_F11_operator_history_and_artifact_commands.md` -> `tests/e2e/test_e2e_operator_cli_surface.py`: real history, artifacts, YAML, prompts, docs, and provenance inspection.
- `51_F03_source_discovery_and_loading_pipeline.md` -> `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`: real source discovery through actual compile inputs.
- `52_F03_schema_validation_compile_stage.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real invalid-YAML failure and durable compile-failure diagnostics.
- `53_F03_override_resolution_compile_stage.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real override-resolution stage reads and failure cases.
- `54_F03_hook_expansion_and_policy_resolution_compile_stage.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real hook and policy expansion visible in compiled outputs.
- `55_F03_rendering_and_compiled_payload_freeze_stage.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real compiled prompt/command payload inspection.
- `56_F03_compiled_workflow_persistence_and_failure_diagnostics.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real persisted compiled workflows and compile failures.
- `60_F05_builtin_node_task_layout_library_authoring.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real built-in layouts and task/subtask chains from authored YAML.
- `61_F05_builtin_validation_review_testing_docs_library_authoring.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real built-in quality/doc definitions selected in a live run.
- `62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real built-in policies/hooks/prompts loaded and selected.
- `63_F03_candidate_and_rebuild_compile_variants.md` -> `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`: real candidate and rebuild compile variant inspection.
- `66_F05_execution_orchestration_and_result_capture.md` -> `tests/e2e/test_e2e_core_orchestration_runtime.py`: real execution-result capture, attempt history, and runtime outcomes.

### Session, recovery, child runtime, and intervention surfaces

- `11_F08_dependency_graph_and_admission_control.md` -> `tests/e2e/test_e2e_dependency_and_child_materialization_real.py`: real dependency-blocked admission and blocker inspection.
- `16_F12_session_binding_and_resume.md` -> `tests/e2e/test_e2e_session_binding_and_resume_real.py`: real bind/show/resume lifecycle through CLI and daemon.
- `17_F34_provider_agnostic_session_recovery.md` -> `tests/e2e/test_e2e_session_binding_and_resume_real.py`: real stale-session recovery using durable state.
- `18_F13_idle_detection_and_nudge_behavior.md` -> `tests/e2e/test_e2e_tmux_session_runtime_real.py`: real idle detection and nudge/escalation through the session backend.
- `19_F14_optional_pushed_child_sessions.md` -> `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`: real pushed child session lifecycle and result collection.
- `20_F15_child_node_spawning.md` -> `tests/e2e/test_e2e_dependency_and_child_materialization_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real child materialization and scheduling, including descent from epic to phase to plan to task.
- `21_F16_manual_tree_construction.md` -> `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`: real manual child creation and authority-mode inspection.
- `22_F20_conflict_detection_and_resolution.md` -> `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py` and `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`: runtime conflict surfacing plus git-backed conflict resolution.
- `23_F18_child_merge_and_reconcile_pipeline.md` -> `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real child result collection and parent reconciliation, with the full-tree suite now also proving hierarchy-wide reset-and-replay mergeback after a second authoritative task revision.
- `24_F19_regeneration_and_upstream_rectification.md` -> `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real subtree regeneration and upstream rectification, with the full-tree suite now covering the modify-phase, rebuild-upward, stale-content reset, and grouped ancestor cutover narrative.
- `29_F24_user_gating_and_pause_flags.md` -> `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`: real pause gate, approval, and resume path.
- `30_F25_failure_escalation_and_parent_decision_logic.md` -> `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`: real child failure, parent decision, durable counters, and decision history.
- `36_F33_optional_isolated_runtime_environments.md` -> `tests/e2e/test_e2e_session_binding_and_resume_real.py` or dedicated environment suite if runtime isolation becomes first-class enough to require it.
- `39_F12_tmux_session_manager.md` -> `tests/e2e/test_e2e_tmux_session_runtime_real.py`: real tmux-backed session launch, attach, and inspection.
- `40_F13_idle_screen_polling_and_classifier.md` -> `tests/e2e/test_e2e_tmux_session_runtime_real.py`: real screen polling and classification evidence.
- `50_F12_session_attach_resume_and_control_commands.md` -> `tests/e2e/test_e2e_session_binding_and_resume_real.py`: real session attach, show-current, resume, nudge, and control commands.
- `64_F08_F15_richer_child_scheduling_and_blocker_explanation.md` -> `tests/e2e/test_e2e_dependency_and_child_materialization_real.py`: richer blocked-child and blocker explanation narratives.
- `65_F04_layout_replacement_and_hybrid_reconciliation.md` -> `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`: real hybrid authority and layout-replacement decisions.
- `67_F12_provider_specific_session_recovery_surface.md` -> `tests/e2e/test_e2e_provider_recovery_real.py`: provider-aware recovery path, gated by provider requirements.
- `68_F25_failure_taxonomy_and_parent_decision_matrix.md` -> `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`: real failure classes and richer parent decision matrix.
- `70_F19_live_rebuild_cutover_coordination.md` -> `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`: real runtime blockers, rebuild coordination, and cutover-readiness behavior.
- `72_F13_expanded_human_intervention_matrix.md` -> `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`: real intervention catalog/apply paths beyond pause approval.
- `77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real sibling dependency unblock only after daemon-applied incremental merge.
- `78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real stale-child refresh onto the merged parent head before the dependent child advances.
- `79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real daemon background merge-lane progression plus dependent child auto-start after refresh.

### Quality, prompt, provenance, documentation, database-history, and audit surfaces

- `06_F27_source_document_lineage.md` -> `tests/e2e/test_e2e_provenance_and_docs_real.py`: real workflow source lineage captured from real compile inputs.
- `25_F21_validation_framework.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real validation gate pass/fail in a live run.
- `26_F22_review_framework.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real review gate outcomes and durable results.
- `27_F26_hook_system.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real hook execution through an actual quality or lifecycle run.
- `28_F23_testing_framework_integration.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real testing gate execution and durable result history.
- `31_F28_prompt_history_and_summary_history.md` -> `tests/e2e/test_e2e_prompt_and_summary_history_real.py`: real prompt delivery and summary registration/history.
- `32_F30_code_provenance_and_rationale_mapping.md` -> `tests/e2e/test_e2e_provenance_and_docs_real.py`: real provenance refresh and rationale inspection after live work.
- `33_F29_documentation_generation.md` -> `tests/e2e/test_e2e_provenance_and_docs_real.py`: real docs build/list/show after live work.
- `35_F36_auditable_history_and_reproducibility.md` -> `tests/e2e/test_e2e_audit_and_reproducibility_real.py`: real reconstructible node/run audit snapshots.
- `42_F05_subtask_library_authoring.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real subtasks selected and executed in live runs.
- `43_F05_prompt_pack_authoring.md` -> `tests/e2e/test_e2e_prompt_and_summary_history_real.py`: real prompt-pack assets delivered through the runtime.
- `44_F04_validation_review_testing_docs_rectification_schema_families.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: real higher-order YAML families selected through compile/runtime behavior.
- `45_F04_runtime_policy_and_prompt_schema_families.md` -> `tests/e2e/test_e2e_prompt_and_summary_history_real.py`: real runtime policy and prompt reference behavior.
- `57_F31_database_runtime_state_schema_family.md` -> `tests/e2e/test_e2e_audit_and_reproducibility_real.py`: real runtime-state views and durable inspection after live work.
- `58_F31_database_session_attempt_history_schema_family.md` -> `tests/e2e/test_e2e_prompt_and_summary_history_real.py` and `tests/e2e/test_e2e_session_binding_and_resume_real.py`: real session/attempt history and prompt/summary audit rows.
- `59_F30_database_provenance_docs_audit_schema_family.md` -> `tests/e2e/test_e2e_audit_and_reproducibility_real.py`: real provenance/docs/audit views after live runs.
- `69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md` -> `tests/e2e/test_e2e_quality_chain_real.py`: one real end-to-end quality-chain narrative.
- `73_F30_multilanguage_provenance_expansion.md` -> `tests/e2e/test_e2e_provenance_and_docs_real.py`: real JS/TS plus Python provenance extraction in a live workspace.

### Git, branch, rectification, merge, and cutover surfaces

- `12_F17_deterministic_branch_model.md` -> `tests/e2e/test_e2e_branch_identity_and_history_real.py`: real branch naming, seed/final commit tracking, and durable branch metadata.
- `22_F20_conflict_detection_and_resolution.md` -> `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`: real merge conflict creation, pause, inspection, and resolution.
- `23_F18_child_merge_and_reconcile_pipeline.md` -> `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real child mergeback through a live repo, including hierarchy-wide task -> plan -> phase -> epic propagation through the authoritative incremental merge lane.
- `24_F19_regeneration_and_upstream_rectification.md` -> `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real rectification and resulting branch/history state, including the passing merged-phase rewrite and rollback/reset narrative in the full-tree suite.
- `32_F30_code_provenance_and_rationale_mapping.md` -> `tests/e2e/test_e2e_branch_identity_and_history_real.py`: provenance continuity across real branch evolution where applicable.
- `35_F36_auditable_history_and_reproducibility.md` -> `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`: reconstructible history across real rebuild/cutover work.
- `59_F30_database_provenance_docs_audit_schema_family.md` -> `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`: durable audit and provenance/docs history after real git flows.
- `70_F19_live_rebuild_cutover_coordination.md` -> `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`: real cutover blockers and cutover behavior.
- `83_F19_dependency_aware_regeneration_scope.md` -> `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`: real rectify-upstream scope selection, candidate replay classification visibility, and dependency-invalidated sibling candidate propagation into rebuilt parent lineages.
- `84_F19_dependency_invalidated_node_fresh_rematerialization.md` -> `tests/e2e/test_flow_10_regenerate_and_rectify_real.py` and `tests/e2e/test_e2e_incremental_parent_merge_real.py`: Flow 10 proves the reachable regenerate/rectify lineage reset and grouped-cutover prerequisites, and the incremental-parent-merge suite now proves all real authoritative follow-on paths implemented today: layout-authoritative dependents rematerialize a fresh layout-owned child tree after grouped cutover, prior-manual dependents remain blocked until real `preserve_manual` reconciliation is applied on the empty fresh version, and prior-manual dependents can also clear that rebuild gate by creating new manual children on the fresh version.
- `85_F19_version_consistent_live_runtime_authority.md` -> `tests/e2e/test_flow_10_regenerate_and_rectify_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real authoritative-version remap through rebuild flows plus full-tree authoritative lineage inspection after daemon-owned propagation.
- `71_F11_live_git_merge_and_finalize_execution.md` -> `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real merge/finalize end to end, including hierarchy-wide finalize after daemon-owned incremental propagation in the full-tree suite.
- `74_F08_F18_incremental_parent_merge_overview.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real happy-path, conflict-resolution, restart-safe incremental merge-backed sibling unblock, and hierarchy-wide authoritative propagation through the full-tree suite.
- `75_F08_F18_incremental_parent_merge_phase_01_durable_merge_lane_scaffolding.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real durable merge-lane state visible through merge events, dependent-child progression, and post-restart completed-unmerged recovery.
- `76_F18_incremental_parent_merge_phase_02_one_child_incremental_merge_execution.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real one-child incremental merge execution into the parent repo and audit surfaces.
- `79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real daemon background merge-lane progression, post-restart resumption, plus dependent child auto-start after refresh.
- `80_F20_incremental_parent_merge_phase_06_conflict_handoff_and_prompt_context.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real conflicted incremental merge handoff, parent-repo manual resolution, durable `resolve_conflict`, and dependent-child unblock on the existing intervention path.
- `81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py`: real parent `child-results` / `reconcile` surfaces now read already-applied merge history on the happy path.
- `82_F08_F18_incremental_parent_merge_full_e2e.md` -> `tests/e2e/test_e2e_incremental_parent_merge_real.py` and `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`: real happy-path, stale-refresh, conflict-resolution, restart-recovery, post-merge reconcile, and hierarchy-wide task -> plan -> phase -> epic propagation checkpoints now exist.

## Exit Criteria

- every existing feature plan appears in this matrix
- every feature has at least one explicit real-code E2E suite target
- future E2E implementation work can proceed by suite family without losing feature-level traceability
