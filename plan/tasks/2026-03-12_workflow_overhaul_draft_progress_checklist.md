# Task: Workflow Overhaul Draft Progress Checklist

## Goal

Add a progression checklist next to the workflow-overhaul draft README so the primary execution queue can be tracked as work moves from waiting to done.

## Rationale

- Rationale: The draft README now defines the execution order, but there is no adjacent tracking surface for plan progression.
- Reason for existence: This task exists to add a lightweight plan-progression checklist for the primary workflow-overhaul draft queue.

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

## Scope

- Database: not applicable for runtime behavior.
- CLI: not applicable for runtime behavior.
- Daemon: not applicable for runtime behavior.
- YAML: not applicable for runtime behavior.
- Prompts: not applicable for runtime behavior.
- Tests: run the task-plan and document-schema verification surface after adding the checklist.
- Performance: not applicable.
- Notes: add the checklist file, reference it from the draft README, and record the work in the development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a progression checklist exists next to `plan/future_plans/workflow_overhaul/draft/README.md`
- the checklist tracks the primary execution queue in order
- the checklist has columns for name/id, execution status, blocked by, secondary status/context, and notes
- the required development log records the change and verification result
