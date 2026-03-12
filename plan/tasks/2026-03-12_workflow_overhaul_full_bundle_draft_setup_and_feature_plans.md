# Task: Workflow Overhaul Full Bundle Draft Setup And Feature Plans

## Goal

Break the entire workflow-overhaul future-plan bundle into draft setup plans and draft feature plans.

## Rationale

- Rationale: The workflow-overhaul bundle had many draft notes and asset directories, but it was not yet broken out into a full setup-plan and feature-plan structure.
- Reason for existence: This task exists to convert the whole bundle into a draft planning family that is closer to implementation-ready form.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_execution_mode_feature_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_execution_mode_flow_impact.md`

## Scope

- Database: draft plans should identify persistence-heavy slices explicitly.
- CLI: draft plans should identify operator and AI-facing surface slices explicitly.
- Daemon: draft plans should identify orchestration and enforcement slices explicitly.
- YAML: draft plans should identify schema and builtin-asset slices explicitly.
- Prompts: draft plans should identify prompt-adoption and prompt-delivery slices explicitly.
- Tests: run the task-plan and document-schema verification surface after adding the new planning artifacts.
- Performance: keep the draft plans concise and slice-oriented.
- Notes: add the draft setup-plan directory, draft feature-plan directory, plan index, and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul folder has a draft setup-plan family
- the workflow-overhaul folder has a draft feature-plan family for the whole bundle
- the setup/feature families cover both workflow-profile and checklist slices
- the required development log records the work and verification result
