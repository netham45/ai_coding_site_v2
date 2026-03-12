# Task: Workflow Overhaul Per-Route E2E Draft Plans

## Goal

Write one draft plan file per workflow-overhaul E2E route.

## Rationale

- Rationale: The route inventory existed as one summary note, but that still left the future E2E work collapsed into one document instead of separate implementation-sized route plans.
- Reason for existence: This task exists to break the workflow-overhaul E2E route set into one draft plan per route so later implementation can pick them up independently.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_workflow_overhaul_e2e_route_plan.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`

## Scope

- Database: per-route planning should identify where durable state and blocked reasons matter.
- CLI: per-route planning should identify which CLI surfaces are part of the route.
- Daemon: per-route planning should identify the daemon-owned legality and mutation boundaries under proof.
- YAML: per-route planning should assume workflow-profile and layout assets are part of the future runtime path.
- Prompts: per-route planning should note prompt-stack or brief surfaces where applicable.
- Tests: create one draft plan file per route.
- Performance: keep each route plan concise and implementation-sized.
- Notes: add the per-route draft-plan directory and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a dedicated directory exists for workflow-overhaul E2E route draft plans
- each planned route has its own draft plan file
- the required development log records the work and verification result
