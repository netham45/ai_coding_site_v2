# Development Log: Real E2E Failure Flow 22 Dependency Gate

## Entry 1

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, tests, notes
- Summary: Recorded the real runtime failure discovered after removing the last lifecycle-forcing shortcut from Flow 22 without attempting a product fix.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/logs/e2e/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py -q`
- Result: Failed in `24.63s`. After the test was rewritten around real parent workflow start and real child materialization, the dependency-blocked `implementation` sibling was still admitted by `node run start` before the `discovery` sibling completed. The observed failure was `assert blocked_start_result.exit_code != 0`, but the real CLI returned success from `POST /api/node-runs/start`.
- Next step: Investigate whether dependency blockers are not enforced during node-run admission for materialized siblings or whether the dependency-status and run-start surfaces have drifted in contract.

## Entry 2

- Timestamp: 2026-03-12
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, prompts, sessions, tests, notes
- Summary: Tightened Flow 22 further by removing the manual `node materialize-children` step and requiring the parent tmux/Codex session itself to create the sibling phases before dependency gating and live completion assertions continue.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py -q`
- Result: Failed in `125.18s`. The converted test no longer relies on manual sibling creation, but the live parent tmux/Codex session never created the sibling phases. `tree show --node <parent> --full` remained a single-node epic tree, and the captured pane showed the session writing `summaries/failure.md` for an `execute_node.run_leaf_prompt` failure instead of driving child creation.
- Next step: Fix the live parent-session child-creation/decomposition path so the sibling phases exist without test-side `node materialize-children`, then rerun Flow 22 to see whether the downstream dependency-admission bug still reproduces on a fully real path.
