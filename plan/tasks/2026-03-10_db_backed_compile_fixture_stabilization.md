# Task: DB-Backed Compile Fixture Stabilization

## Goal

Stabilize the migrated test-database fixture path used by DB-backed workflow compile tests so daemon/API compile proof can rely on real migrated schema state without intermittent `node_hierarchy_definitions` visibility failures.

## Rationale

- Rationale: The scoped parent decomposition phase now has bounded prompt and override-resolution proof, but the next honest proving layer needs real DB-backed compile coverage.
- Reason for existence: Current attempts to add daemon/API compile proof are blocked by fixture-level instability where migrated tests can still fail with `relation "node_hierarchy_definitions" does not exist`, which makes the proof surface unreliable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/05_F04_immutable_workflows.md`
- `plan/tasks/2026-03-10_scoped_parent_decomposition_runtime_phase.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/implementation/automated_full_tree_cat_runtime_preimplementation_note.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: inspect the migrated schema fixture, engine/session-factory lifetime, and any migration visibility/race issues affecting DB-backed compile tests.
- CLI: no CLI contract changes are intended in this remediation unless the fixture problem reveals a CLI/bootstrap mismatch.
- Daemon: reconcile any `create_app()` or compile-path assumptions about schema availability if they differ from the migrated fixture contract.
- YAML: no YAML behavior change is intended.
- Prompts: no prompt behavior change is intended.
- Tests: add or adjust bounded regression coverage that proves migrated DB-backed compile tests can see the hierarchy tables reliably.
- Performance: keep fixture setup deterministic without adding unnecessary heavyweight per-test bootstrapping.
- Notes: document the real proving boundary and any fixture invariants discovered while stabilizing this path.

## Plan

### Phase A: Reproduce and localize the fixture failure

1. Reproduce the `node_hierarchy_definitions` visibility failure with the smallest DB-backed compile test.
2. Compare passing DB-backed tests against the failing compile path to identify engine, migration, or transaction-lifetime differences.
3. Determine whether the defect is in the fixture, migration/bootstrap sequence, or test usage.

Exit criteria:

- the failure is reproducible on demand with a narrow command
- the responsible layer is identified concretely

### Phase B: Fix the fixture/runtime mismatch

1. Implement the narrowest reliable fix for the migrated schema visibility problem.
2. Keep the existing test architecture intact unless the root cause requires a broader fixture change.
3. Add a bounded regression test or strengthen an existing fixture-architecture test so the mismatch does not silently return.

Exit criteria:

- DB-backed compile tests can see `node_hierarchy_definitions` reliably through the documented fixture path
- the fix is bounded and does not rely on ad hoc per-test workarounds

### Phase C: Re-enable blocked compile proof

1. Restore or add the scoped parent decomposition daemon/API compile proof that was previously blocked.
2. Update notes and logs to describe the repaired proving boundary honestly.

Exit criteria:

- the scoped parent decomposition work can advance to real DB-backed compile proof

## Verification

- `python3 -m pytest tests/unit/test_fixture_architecture.py -q`
- `python3 -m pytest tests/unit/test_workflows.py -q`
- `python3 -m pytest tests/integration/test_daemon.py -k "workflow_compile and register_layout_endpoint" -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The migrated DB-backed test fixture reliably exposes the hierarchy tables required for compile-path tests.
- The blocked scoped parent decomposition compile proof can run against the real migrated DB path.
- Notes and logs record the real cause and the real repaired boundary.
