# Development Log: Refactor E2E Tests To Real Runtime Only

## Entry 1

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: in_progress
- Affected systems: cli, daemon, database, tests, notes
- Summary: Began Phase 1 of the E2E real-runtime refactor by removing the fake default session backend from the shared real-E2E harness and preparing targeted reruns against tmux-backed execution.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/tasks/2026-03-10_e2e_realness_audit.md`
  - `notes/logs/reviews/2026-03-10_e2e_realness_audit.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/contracts/runtime/session_recovery_appendix.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "AICODING_SESSION_BACKEND|session_backend: str = \"fake\"|session_backend=\"tmux\"" tests/helpers/e2e.py tests/fixtures/e2e.py tests/e2e`
- Result: The shared E2E harness and fixture defaults were identified as the first concrete fake-runtime surface to remove.
- Next step: Change the shared harness default from `fake` to `tmux`, then run representative real-E2E tests to confirm the refactor baseline.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: in_progress
- Affected systems: cli, daemon, database, tests, notes
- Summary: Switched the shared real-E2E harness default from `fake` to `tmux`, verified that `tmux` is available, and reran one non-session and one tmux-backed E2E flow successfully.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `tmux -V`
  - `python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q`
  - `python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q`
- Result: Passed. The shared E2E harness is no longer fake by default, and representative real-E2E flows still pass under the tmux-backed session posture.
- Next step: Continue Phase 2 by triaging and rewriting or removing the invalid E2E files that still rely on direct DB/API shortcuts or lifecycle-transition forcing.

## Entry 3

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: in_progress
- Affected systems: cli, daemon, database, tests, notes
- Summary: Rewrote `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` in place so it no longer uses direct DB/API proof or intentional placeholder failures, and refactored Flow 08 to use real parent child-materialization instead of forcing child readiness.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`
  - `python3 -m pytest tests/e2e/test_flow_08_handle_failure_and_escalate_real.py -q`
- Result: Passed. The full-tree file is now a real CLI-only runtime test, and Flow 08 no longer fabricates child readiness via direct lifecycle mutation. Remaining known gap: Flow 11 still forces lifecycle states before finalize/merge, so that gap is now tracked in the checklist.
- Next step: Refactor Flow 11 and any similar git/rectification flows to reach completion through actual runtime work before finalize/cutover commands.

## Entry 4

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: in_progress
- Affected systems: cli, daemon, database, yaml, prompts, tests, notes
- Summary: Refactored Flow 11 to remove lifecycle forcing from the finalize-and-merge narrative, audited the remaining E2E files for direct DB/API or lifecycle shortcuts, and identified Flow 22 as the last remaining lifecycle-forcing runtime shortcut in `tests/e2e/`.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_flow_11_finalize_and_merge_real.py -q`
  - `rg -n 'harness\\.request|create_engine\\(|pytest\\.fail\\(|node\", \"lifecycle\", \"transition' tests/e2e`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_feature_checklist_docs.py -q`
- Result: Passed. Flow 11 now uses real git/runtime progression, and the remaining E2E shortcut audit narrowed to Flow 22 as the last file still forcing lifecycle state in the `tests/e2e/` family.
- Next step: Rewrite Flow 22 around real parent workflow start, real child materialization, and live tmux completion; then rerun the targeted provider-backed E2E flow and update the gap checklist based on the observed environment result.

## Entry 5

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, yaml, prompts, tests, notes
- Summary: Removed the last `node lifecycle transition` shortcut from Flow 22, confirmed the `tests/e2e/` family no longer contains the direct DB/API, placeholder-failure, or lifecycle-transition patterns from the earlier audit, and then hit a real runtime dependency-admission failure in the provider-backed sibling-wait flow.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n 'harness\\.request|create_engine\\(|pytest\\.fail\\(|node\", \"lifecycle\", \"transition' tests/e2e`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_feature_checklist_docs.py -q`
  - `python3 -m pytest tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py -q`
- Result: The audit grep is clean, and the document consistency suite passed. Flow 22 now uses only real runtime commands, but it fails against the current product because the dependency-blocked sibling is still admitted by `node run start` before the prerequisite sibling completes. That product/runtime gap is recorded separately in `notes/logs/e2e/2026-03-10_real_e2e_failure_flow22_dependency_gate.md`.
- Next step: Continue targeted provider-backed reruns for the remaining real E2E flows while leaving the Flow 22 runtime dependency-gate bug explicitly logged for a later product fix.

## Entry 6

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, prompts, sessions, tests, notes
- Summary: Continued the targeted provider-backed reruns after logging the Flow 22 dependency-gate issue and discovered a second real runtime failure in the child-session mergeback flow.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_feature_checklist_docs.py -q`
  - `python3 -m pytest tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q`
- Result: The document consistency suite passed again. Flow 21 failed in the real provider-backed child-session path because the delegated tmux child session received raw prompt text with an unresolved `{{node_id}}` placeholder and never produced a durable merge-back result. That runtime gap is recorded separately in `notes/logs/e2e/2026-03-10_real_e2e_failure_flow21_child_session_mergeback.md`.
- Next step: Keep moving through provider-independent real E2E slices while leaving the broken child-session bootstrap and dependency-admission product gaps explicitly tracked for later product fixes.

## Entry 7

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, yaml, tests, notes
- Summary: Continued the real E2E sweep with the compile-failure diagnostics flow and found another runtime/contract mismatch after removing fake-runtime assumptions from the overall suite.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q`
- Result: Flow 20 failed in the real daemon path because `workflow source-discovery` returned `404 compiled workflow not found` immediately after a failed compile, even though compile-failure diagnostics were still available. That runtime or contract gap is recorded separately in `notes/logs/e2e/2026-03-10_real_e2e_failure_flow20_compile_source_discovery.md`.
- Next step: Continue targeted reruns for the remaining real E2E flows while accumulating the current real-runtime gap inventory instead of weakening the tests back toward shortcut or simulated proof.

## Entry 8

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: changed_plan
- Affected systems: cli, daemon, database, prompts, sessions, tests, notes
- Summary: Tightened the governing plan and checklist after confirming that several currently passing E2E files still rely on operator-driven workflow progression rather than live runtime execution.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n 'subtask\\s*\",\\s*\"(start|complete|fail)|summary\\s*\",\\s*\"register|workflow\\s*\",\\s*\"advance|session\\s*\",\\s*\"pop|respond-to-child-failure' tests/e2e`
- Result: The audit confirmed that multiple E2E files still manually drive workflow state even though they no longer use fake backends or direct DB/API proof. Those files are now explicitly tracked as not meeting the stricter “live runtime only” bar.
- Next step: Refactor or quarantine the operator-driven E2E files one by one until the remaining passing set only contains tests where the runtime, not the test, advances the workflow.

## Entry 9

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, prompts, sessions, tests, notes
- Summary: Rewrote Flow 05 to stop manually advancing the run and instead require durable progress from the live primary tmux/Codex session.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_feature_checklist_docs.py -q`
- Result: The document consistency suite passed. The rewritten Flow 05 failed in the real runtime path because the primary tmux/Codex session never produced durable attempt, summary, or completed-subtask state, and tmux eventually vanished while the daemon still reported the run as active. That runtime gap is recorded separately in `notes/logs/e2e/2026-03-10_real_e2e_failure_flow05_primary_session_progress.md`.
- Next step: Continue rewriting the remaining operator-driven E2E files to require live runtime progress and log each resulting product/runtime gap instead of allowing manual advancement to mask it.
