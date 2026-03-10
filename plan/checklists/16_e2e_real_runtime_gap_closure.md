# Checklist C16: E2E Real Runtime Gap Closure

## Goal

Track the remaining gaps that still prevent the `tests/e2e/` family from being uniformly “real command, verify real state” proof.

## Required References

- `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
- `plan/tasks/2026-03-10_e2e_realness_audit.md`
- `notes/logs/reviews/2026-03-10_e2e_realness_audit.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Verify

- shared harness defaults do not silently use fake backends
- no E2E file relies on direct DB/API shortcut proof as its primary narrative
- no E2E file intentionally fails as a placeholder
- lifecycle progression is proven through actual runtime commands rather than manual transition shortcuts
- no E2E file manually advances subtasks or injects outputs as a stand-in for live AI/runtime execution
- git/finalize and rectification flows use real runtime progression before finalize/cutover actions

## Tests

- targeted reruns of refactored E2E files
- non-gated real-E2E sweep
- gated tmux/git reruns for files still under refactor

## Canonical Review Rule

- use `notes/catalogs/checklists/verification_command_catalog.md` for the canonical command set
- use `notes/catalogs/checklists/e2e_execution_policy.md` for gating and execution-tier expectations
- keep gaps explicit until the actual runtime shortcut has been removed and the affected test rerun successfully

## Notes

- Closed:
  - shared E2E harness fake default removed; tmux is now the default harness posture
  - `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py` no longer manually issues `subtask start`, `summary register`, `subtask complete`, or `workflow advance`; it now waits for live primary-session progress
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` rewritten in place as a passing CLI-only real runtime narrative
  - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py` rewritten to use parent child-materialization instead of forcing child readiness
  - `tests/e2e/test_flow_11_finalize_and_merge_real.py` rewritten to reach finalize and merge through real git/runtime progression instead of lifecycle forcing
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py` rewritten to use real parent workflow start plus child materialization instead of forcing sibling readiness
- Open:
  - `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py` now exposes a real runtime gap: the primary tmux/Codex session can disappear without durable attempt, summary, or completed-subtask state being recorded
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` still manually issues `subtask start`, `summary register`, `subtask complete`, and `workflow advance`; it is not acceptable as full real-workflow proof
  - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py` still manually issues `subtask start` and `subtask fail`; it proves operator failure handling, not live child execution
  - `tests/e2e/test_flow_09_run_quality_gates_real.py` still loops through manual `subtask complete` and `workflow advance` calls to reach quality stages; it is not acceptable as full real-workflow proof
  - `tests/e2e/test_flow_13_human_gate_and_intervention_real.py` still loops through manual `subtask complete` and `workflow advance` calls to reach the human pause gate; it is not acceptable as full real-workflow proof
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py` now exposes a real runtime/contract gap: after a failed compile, `workflow source-discovery` returns `compiled workflow not found` instead of remaining inspectable through the CLI
  - `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py` now exposes a real runtime gap: the delegated child tmux session receives raw prompt text with an unresolved `{{node_id}}` placeholder and never produces a durable merge-back result
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py` now exposes a real runtime gap: the dependency-blocked sibling is still admitted by `node run start` before the prerequisite sibling completes
  - provider-backed tmux flows still need targeted reruns beyond Flow 22 to confirm they pass without any remaining runtime-surface shortcuts
