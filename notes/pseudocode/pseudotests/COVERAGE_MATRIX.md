# Pseudotest Coverage Matrix

## Purpose

Map every authored module and state machine in `notes/pseudocode/` to at least one pseudotest suite and representative cases.

Use this file to identify missing coverage quickly.

---

## Coverage status

`covered` means at least one explicit pseudotest case targets the artifact.

| Artifact | Type | Primary test file | Representative cases | Status |
| --- | --- | --- | --- | --- |
| `modules/compile_workflow.md` | module | `pseudotests/runtime_core_tests.md` | `compile_accepts_valid_workflow_inputs`, `compile_rejects_invalid_override_target`, `compile_rejects_invalid_dependency_graph`, `compile_failed_node_cannot_be_admitted_or_run` | covered |
| `modules/check_node_dependency_readiness.md` | module | `pseudotests/runtime_core_tests.md` | `admission_blocks_unsatisfied_dependencies`, `failed_compile_never_admits_run` | covered |
| `modules/admit_node_run.md` | module | `pseudotests/runtime_core_tests.md` | `admission_blocks_non_ready_node`, `admission_blocks_unsatisfied_dependencies`, `admission_allows_ready_unblocked_node`, `failed_compile_never_admits_run` | covered |
| `modules/run_node_loop.md` | module | `pseudotests/runtime_core_tests.md` | `node_loop_advances_after_successful_subtask`, `node_loop_pauses_on_human_gate`, `node_loop_finalizes_when_cursor_exhausted`, `paused_for_user_does_not_resume_implicitly` | covered |
| `modules/execute_compiled_subtask.md` | module | `pseudotests/runtime_core_tests.md` | `node_loop_advances_after_successful_subtask`, `subtask_failure_records_summary_and_blocks_progress` | covered |
| `modules/handle_subtask_failure.md` | module | `pseudotests/runtime_core_tests.md` | `retry_budget_exhaustion_escalates_to_parent_or_operator` | covered |
| `modules/recover_interrupted_run.md` | module | `pseudotests/runtime_core_tests.md` | `recovery_reuses_existing_healthy_session_when_safe`, `recovery_creates_replacement_session_when_tmux_is_lost`, `recovery_refuses_non_resumable_run` | covered |
| `modules/materialize_layout_children.md` | module | `pseudotests/orchestration_and_state_tests.md` | `layout_authoritative_parent_materializes_valid_child_set`, `hybrid_parent_blocks_silent_structural_replacement`, `invalid_layout_cycle_fails_before_child_creation` | covered |
| `modules/schedule_ready_children.md` | module | `pseudotests/orchestration_and_state_tests.md` | `ready_child_is_not_blocked_by_unrelated_incomplete_sibling`, `already_running_child_is_not_restarted`, `impossible_wait_is_not_treated_as_normal_block` | covered |
| `modules/wait_for_child_completion.md` | module | `pseudotests/orchestration_and_state_tests.md` | `impossible_wait_is_not_treated_as_normal_block`, `parent_reaches_reconcile_ready_only_when_required_children_complete` | covered |
| `modules/collect_child_results.md` | module | `pseudotests/orchestration_and_state_tests.md` | `parent_reaches_reconcile_ready_only_when_required_children_complete`, `child_result_collection_uses_authoritative_version_only`, `failed_candidate_does_not_contaminate_parent_or_dependency_resolution` | covered |
| `modules/handle_child_failure_at_parent.md` | module | `pseudotests/orchestration_and_state_tests.md` | `parent_retries_child_for_retryable_transient_failure`, `parent_replans_when_child_failure_indicates_bad_layout_or_requirements`, `parent_pauses_when_failure_thresholds_are_exceeded` | covered |
| `modules/regenerate_node_and_descendants.md` | module | `pseudotests/rectification_and_cutover_tests.md` | `candidate_lineage_stays_non_authoritative_during_rebuild`, `failed_candidate_does_not_contaminate_parent_or_dependency_resolution` | covered |
| `modules/rectify_node_from_seed.md` | module | `pseudotests/rectification_and_cutover_tests.md` | `rectification_uses_authoritative_child_finals_only`, `rectification_stops_before_quality_gates_when_merge_conflict_occurs` | covered |
| `modules/finalize_lineage_cutover.md` | module | `pseudotests/rectification_and_cutover_tests.md` | `cutover_requires_full_scope_stability_by_default`, `user_gated_cutover_pauses_before_authority_switch`, `successful_cutover_switches_authority_then_supersedes_old_scope` | covered |
| `modules/update_provenance_for_node.md` | module | `pseudotests/rectification_and_cutover_tests.md` | `provenance_prefers_exact_match_over_heuristic_match`, `provenance_exposes_inference_confidence_when_rename_or_move_is_assumed` | covered |
| `state_machines/node_lifecycle.md` | state_machine | `pseudotests/orchestration_and_state_tests.md` | `compile_failed_node_cannot_be_admitted_or_run`, `paused_for_user_does_not_resume_implicitly`, `superseded_node_cannot_return_to_active_execution` | covered |
| `state_machines/parent_child_authority.md` | state_machine | `pseudotests/orchestration_and_state_tests.md` | `hybrid_parent_blocks_silent_structural_replacement`, `parent_replans_when_child_failure_indicates_bad_layout_or_requirements` | covered |
| `state_machines/lineage_authority.md` | state_machine | `pseudotests/rectification_and_cutover_tests.md` | `candidate_lineage_stays_non_authoritative_during_rebuild`, `failed_candidate_does_not_contaminate_parent_or_dependency_resolution`, `child_result_collection_uses_authoritative_version_only` | covered |
| `state_machines/workflow_events.md` | state_machine | `pseudotests/runtime_core_tests.md` | `all_critical_runtime_transitions_are_queryable`, `node_loop_pauses_on_human_gate`, `recovery_reuses_existing_healthy_session_when_safe`, `successful_cutover_switches_authority_then_supersedes_old_scope` | covered |

---

## Current result

All authored modules and state machines are now covered by at least one explicit pseudotest case.

The remaining gap is not basic coverage. It is standardization and evaluation:

- converting existing suites fully into the canonical format from `TEST_FORMAT.md`
- optionally adding pass/fail review records for each case
- eventually translating this markdown structure into a machine-readable schema if you want a pseudotest runner
