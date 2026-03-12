# Task: Workflow Overhaul Checklist And E2E Subfeature Breakdown

## Goal

Expand the checklist and E2E draft plan families into deeper file-per-child breakdowns so they match the planning depth of the workflow-profile side.

## Rationale

- Rationale: The checklist and E2E route families are still coarse compared with the workflow-profile child-plan family.
- Reason for existence: This task exists to add narrower child-plan assets and indexes so those families can be executed and decomposed at the same granularity.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_workflow_overhaul_e2e_route_plan.md`

## Scope

- Database: the deeper breakdown should isolate checklist persistence and E2E route proving slices that touch durable state.
- CLI: the deeper breakdown should isolate operator and inspection slices for checklist and route proving work.
- Daemon: the deeper breakdown should isolate orchestration, legality, and route-runtime proving slices.
- YAML: the deeper breakdown should isolate checklist schema/template and profile-driven route setup slices.
- Prompts: the deeper breakdown should isolate checklist prompt delivery and prompt-aware route proving slices.
- Tests: run the task-plan and document-schema verification surface after adding the new child-plan families and indexes.
- Performance: keep the child-plan files concise and implementation-sized.
- Notes: add the deeper checklist/E2E child-plan directories, indexes, README updates, and development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the checklist family has a deeper child-plan directory with file-per-child assets
- the E2E route family has a deeper child-plan directory with file-per-child assets
- the `draft/` README and related indexes explain how those new child-plan families fit into execution
- the required development log records the work and verification result
