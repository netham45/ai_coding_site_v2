# Phase E2E-03: E2E Session, Recovery, And Child Runtime

## Goal

Create real E2E suites for session management, recovery, dependency handling, child scheduling, reconciliation, failure handling, and human-intervention runtime behavior.

## Rationale

- Rationale: Session ownership, child execution, pause/recovery, and failure escalation are some of the most orchestration-specific behaviors in the repository and are the least acceptable to leave at bounded or simulated proof.
- Reason for existence: This phase exists to prove that real runtime coordination survives through real session, dependency, child, and intervention boundaries.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/19_F14_optional_pushed_child_sessions.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/21_F16_manual_tree_construction.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/29_F24_user_gating_and_pause_flags.md`
- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`
- `plan/features/36_F33_optional_isolated_runtime_environments.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/40_F13_idle_screen_polling_and_classifier.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`
- `plan/features/67_F12_provider_specific_session_recovery_surface.md`
- `plan/features/68_F25_failure_taxonomy_and_parent_decision_matrix.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/72_F13_expanded_human_intervention_matrix.md`

## Required Notes

- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: assert real durable session binding, recovery state, child scheduling state, dependency blockers, parent decisions, intervention records, and rebuild coordination state.
- CLI: drive attach/resume/control, child management, pause/intervention, and inspection commands through the real CLI subprocess path.
- Daemon: use the real daemon process, real session backend where required by the feature family, and real API boundaries.
- YAML: exercise layout, runtime policy, failure policy, and reconciliation policy behavior through actual runtime materialization and control.
- Prompts: exercise recovery, pause, delegated-child, idle-nudge, and intervention-related prompt delivery/history where applicable.
- Notes: document which session/recovery suites require tmux, provider credentials, or isolated environments.
- Tests: separate provider-agnostic, tmux-backed, and provider-backed E2E suites so requirements remain explicit.
- Performance: keep recovery waits bounded and deterministic where possible.

## Proposed Suite Families

- `tests/e2e/test_e2e_session_binding_and_resume_real.py`
- `tests/e2e/test_e2e_tmux_session_runtime_real.py`
- `tests/e2e/test_e2e_dependency_and_child_materialization_real.py`
- `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`
- `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`
- `tests/e2e/test_e2e_rebuild_coordination_and_cutover_real.py`

## Exit Criteria

- session, recovery, child, and intervention features are proven through real code paths
- bounded helper-only proof is no longer the strongest claim for these runtime areas
- suite requirements and skips are explicit rather than implicit
