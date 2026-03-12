# Task: Workflow Overhaul E2E Task Profile Catalog

## Goal

Document the concrete future `task.e2e.*` profile catalog so real runtime journeys and suite families can be assigned as explicit E2E child tasks.

## Rationale

- Rationale: The workflow-overhaul bundle currently has one generic `task.e2e` profile, but the repository's actual runtime and E2E planning surfaces already distinguish many different journeys and suite families.
- Reason for existence: This task exists to make those E2E work packets explicit in the workflow-overhaul future-plan bundle so later profile-aware decomposition can assign them as dedicated tasks rather than generic proof placeholders.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/task.e2e.yaml`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/task_profiles.md`

## Scope

- Database: not directly affected beyond documenting which E2E tasks prove durable runtime state.
- CLI: document E2E profiles around real CLI-driven runtime journeys.
- Daemon: document E2E profiles around real daemon-owned runtime journeys and suite families.
- YAML: keep the catalog aligned with the base `task.e2e` workflow-profile draft.
- Prompts: no direct prompt edits, but the catalog should assume inheritance from the base E2E prompt contract.
- Tests: align the catalog with existing canonical flows and real-E2E suite targets.
- Performance: keep the catalog compact and indexed by proving surface rather than duplicating entire feature notes.
- Notes: add the E2E task-profile catalog and the required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul bundle has an explicit catalog of concrete `task.e2e.*` profiles
- the catalog distinguishes canonical-flow E2E profiles from specialized suite-family E2E profiles
- the base-to-concrete inheritance rule is documented clearly
- the required development log records the consulted flow and E2E mapping surfaces
