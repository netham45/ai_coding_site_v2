# E2E Execution Policy

## Purpose

This note defines how bounded, integration, performance, and real-E2E verification are expected to run in local development, standard CI, gated/manual runs, and release-readiness review.

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
python3 -m pytest tests/unit
python3 -m pytest tests/integration
python3 -m pytest tests/integration/test_flow_contract_suite.py -q
python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
```

Claim boundary:

- passing this tier can support `implemented`
- it can support `verified` for bounded or integration-only claims
- it cannot support `flow_complete` for a real runtime narrative by itself

### Tier 2: Standard CI

Expected use:

- repository-default pull request validation
- repeatable proof that does not depend on tmux, live git workflows, or provider credentials

Expected command ladder:

```bash
python3 -m aicoding.cli.main admin db ping
python3 -m aicoding.cli.main admin db heads
python3 -m aicoding.cli.main admin db upgrade
python3 -m aicoding.cli.main admin db check-schema
python3 -m pytest tests/unit
python3 -m pytest tests/integration
python3 -m pytest tests/integration/test_flow_contract_suite.py -q
python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
python3 -m pytest tests/performance/test_harness.py -q
```

Environment expectation:

- PostgreSQL service available
- no requirement for tmux
- no requirement for live AI-provider credentials

Claim boundary:

- passing this tier can support `verified` for the bounded, integration, schema, and performance layers it actually proves
- it still does not support `release_ready` or broad real-E2E completion claims by itself

### Tier 3: Gated Real E2E

Expected use:

- manual or gated runs for real daemon/CLI/runtime proof
- feature-family hardening
- pre-release reality checks

Current real-E2E command set:

```bash
python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q
python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q
python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q
python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
python3 -m pytest tests/e2e/test_e2e_operator_cli_surface.py -q
python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q
python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q
```

Current runtime policy:

- the shared real-E2E harness no longer defaults to the fake session backend; tmux-backed session handling is now the default harness posture
- the real E2E harness now creates one database per test, so DB-backed execution is isolated at the database layer
- parallel execution is no longer blocked by the old shared-database fixture
- other real-resource constraints such as tmux, provider credentials, ports, and workspace-heavy narratives may still justify selective or staged parallelism

Additional gated markers:

- `requires_git`: run only when real git execution is available and the target suite actually needs it
- `requires_tmux`: run only when tmux-backed session orchestration is available
- `requires_ai_provider`: run only when live provider credentials and budgets are intentionally supplied

Claim boundary:

- passing a real-E2E checkpoint can support `flow_complete` for the exact narrative it proves
- it does not automatically upgrade adjacent features or broader families beyond the documented scope

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
- Provider-backed, tmux-backed, and live-git-backed suites are gated by explicit environment availability and should not silently downgrade to fake backends.

## Maintenance Rule

If the repo adds a new default CI suite, a new gated real-E2E suite, or a new release-readiness requirement, update this policy and `verification_command_catalog.md` in the same change.
