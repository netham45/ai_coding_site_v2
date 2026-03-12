# E2E Execution Policy

## Purpose

This note defines how bounded, integration, performance, and real-E2E verification are expected to run in local development, standard CI, gated/manual runs, and release-readiness review.

Parallel-safe execution is the default repository expectation across these tiers.

Serial execution may still be used for local debugging, narrower fault isolation, or staged bring-up, but it does not excuse tests that fail because of cross-test interference.

Environment-capability gating is allowed; serialization caused by shared mutable state is a defect.

Use this together with:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Execution Tiers

### Tier 1: Local Default Iteration

Expected use:

- ordinary implementation work
- note and checklist updates
- fast feedback during code changes

Canonical command ladder:

```bash
PYTHONPATH=src python3 -m pytest tests/unit
PYTHONPATH=src python3 -m pytest tests/integration
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_contract_suite.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
```

Claim boundary:

- passing this tier can support `implemented`
- it can support `verified` for bounded or integration-only claims
- it cannot support `flow_complete` for a real runtime narrative by itself
- this tier remains a convenience iteration surface, not a claim that serial-only execution is acceptable

### Tier 2: Standard CI

Expected use:

- repository-default pull request validation
- repeatable proof that does not depend on tmux, live git workflows, or provider credentials

Expected command ladder:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main admin db ping
PYTHONPATH=src python3 -m aicoding.cli.main admin db heads
PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade
PYTHONPATH=src python3 -m aicoding.cli.main admin db check-schema
PYTHONPATH=src python3 -m pytest tests/unit
PYTHONPATH=src python3 -m pytest tests/integration
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_contract_suite.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
PYTHONPATH=src python3 -m pytest tests/performance/test_harness.py -q
PYTHONPATH=src python3 -m pytest tests/unit tests/integration tests/performance -n auto --dist=loadfile -q
```

Environment expectation:

- PostgreSQL service available
- no requirement for tmux
- no requirement for live AI-provider credentials
- parallel bounded-suite execution now expects isolated per-test databases instead of shared `public`-schema resets
- bounded suites are expected to remain worker-safe; any parallel-only failures are open issues rather than accepted CI limitations

Claim boundary:

- passing this tier can support `verified` for the bounded, integration, schema, and performance layers it actually proves
- it still does not support `release_ready` or broad real-E2E completion claims by itself

### Tier 3: Gated Real E2E

Expected use:

- manual or gated runs for real daemon/CLI/runtime proof
- feature-family hardening
- pre-release reality checks

Current passing full-real E2E checkpoint set:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_bootstrap_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_browser_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_operator_cli_surface.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q
```

Current non-canonical real-runtime bring-up targets:

These use the real runtime harness and remain important, but they must not be
treated as passing full-real E2E checkpoints until their workflows satisfy the
live-run-equivalence rule from `AGENTS.md`.

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
```

Current runtime policy:

- the shared real-E2E harness no longer defaults to the fake session backend; tmux-backed session handling is now the default harness posture
- the real E2E harness now creates one database per test, so DB-backed execution is isolated at the database layer
- the real E2E harness now uses a per-test `TMUX_TMPDIR` namespace so default-server tmux state is not shared across tests
- the real E2E harness now reserves the daemon listener socket before process launch and hands that socket to Uvicorn, so parallel startup no longer relies on a free-port probe race
- the website repo-backed project-start browser checkpoint now runs Playwright against the daemon-served compiled frontend rather than the mock-daemon matrix
- parallel execution is no longer blocked by the old shared-database fixture
- staged or selective execution may still be used while diagnosing failures or when explicit environment capabilities are absent, but any eligible test that fails only because of parallel execution remains a defect to fix
- a real harness alone is not enough for canonical E2E status; any workflow that still relies on synthetic progression, lifecycle forcing, or operator/test-side substitutes belongs in the non-canonical bring-up set until rewritten

Additional gated markers:

- `requires_git`: run only when real git execution is available and the target suite actually needs it
- `requires_tmux`: run only when tmux-backed session orchestration is available
- `requires_ai_provider`: run only when live provider credentials and budgets are intentionally supplied

Claim boundary:

- passing a real-E2E checkpoint can support `flow_complete` for the exact narrative it proves
- it does not automatically upgrade adjacent features or broader families beyond the documented scope
- non-canonical bring-up targets do not support `flow_complete`, `verified`, or “fully real E2E” claims for their workflow until they pass with no synthetic workflow steps

### Tier 4: Release-Readiness Review

Expected use:

- hardening or release-candidate review
- explicit review of what is verified today versus still partial or deferred

Required posture:

- Tier 2 passes
- all currently required gated real-E2E checkpoints for the release scope are run successfully
- partial or deferred real-E2E areas are documented plainly
- checklist, command-catalog, and flow-coverage surfaces are current

Claim boundary:

- `release_ready` is allowed only when the release scope has the required bounded, integration, performance, and real-E2E proof documented and actually run

## Environment Rules

- Real PostgreSQL is required for standard CI and real-E2E runs.
- Real daemon subprocess and real CLI invocation are required for real-E2E runs.
- Real-E2E runs now have per-test database isolation; any remaining serialization should be justified by non-database resource constraints rather than shared database state.
- Unit, integration, and performance fixtures now also aim to avoid shared-database mutation by using isolated test databases rather than one shared migrated `public` schema.
- Provider-backed, tmux-backed, and live-git-backed suites are gated by explicit environment availability and should not silently downgrade to fake backends.
- When those required capabilities are present, eligible tests are expected to run safely in parallel.
- If they do not, the result is a correctness gap in isolation or resource ownership that must be tracked and fixed.

## Maintenance Rule

If the repo adds a new default CI suite, a new gated real-E2E suite, or a new release-readiness requirement, update this policy and `verification_command_catalog.md` in the same change.
