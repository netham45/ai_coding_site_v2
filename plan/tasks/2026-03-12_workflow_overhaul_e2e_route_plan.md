# Task: Workflow Overhaul E2E Route Plan

## Goal

Lay out the full workflow-overhaul E2E route set so the future implementation has an explicit end-to-end proving plan.

## Rationale

- Rationale: The workflow-overhaul bundle had a profile E2E matrix, but it still lacked the concrete route plan that says which runtime journeys will exist, what each route must prove, and what adversarial checks belong in each route.
- Reason for existence: This task exists to turn the workflow-overhaul E2E story into a route-level plan rather than leaving it at a profile-to-suite mapping level.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`

## Scope

- Database: route planning must account for durable selected-profile state, blocked reasons, and compiled workflow inspection.
- CLI: route planning must cover real CLI start, inspect, materialize, merge, and blocked-action surfaces.
- Daemon: route planning must cover real daemon-owned legality and blocked-mutation behavior.
- YAML: route planning must assume profile-aware compile and materialization come from declared workflow-profile and layout assets.
- Prompts: route planning must cover prompt-stack and workflow-brief inspection where those are part of the runtime route.
- Tests: define the future real-E2E route set and the proposed suite files that should own each route.
- Performance: group the route set into a small number of high-value suites and keep the plan readable.
- Notes: add the route-planning note and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul bundle has an explicit route-level E2E plan
- each planned route has a stated goal, core assertions, and a future suite file
- rigid workflow enforcement routes are called out explicitly
- the required development log records the consulted notes and verification result
