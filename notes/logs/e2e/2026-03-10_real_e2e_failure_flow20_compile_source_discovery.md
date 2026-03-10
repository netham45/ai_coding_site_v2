# Development Log: Real E2E Failure Flow 20 Compile Source Discovery

## Entry 1

- Timestamp: 2026-03-10
- Task ID: refactor_e2e_tests_to_real_runtime_only
- Task title: Refactor E2E tests to real runtime only
- Status: partial
- Affected systems: cli, daemon, database, yaml, tests, notes
- Summary: Recorded the real runtime failure discovered when exercising compile-failure diagnostics against the actual daemon state without attempting a product fix.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/logs/e2e/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q`
- Result: Failed in `14.18s`. After a real schema-validation compile failure, `workflow compile-failures` still returned data, but `workflow source-discovery --node <id>` returned `404 compiled workflow not found`. The test currently expects source-discovery to remain inspectable after failed compile attempts, so the real CLI/daemon surface does not yet satisfy that E2E expectation.
- Next step: Reconcile whether source-discovery after failed compile is supposed to operate from compile-failure records or whether the CLI/test expectation exceeds the current daemon contract.
