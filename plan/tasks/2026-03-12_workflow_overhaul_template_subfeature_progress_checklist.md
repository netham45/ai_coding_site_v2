# Task: Workflow Overhaul Template Subfeature Progress Checklist

## Goal

Add an explicit progress and dependency checklist for the template subfeature-plan family so the new 40 child plans have a governable status surface.

## Rationale

- Rationale: The template subfeature plans now exist, but they still lack the same explicit status-tracking surface the parent draft queue already has.
- Reason for existence: This task exists to add the missing progress/dependency artifact so the template subfeature family can be sequenced, blocked, and tracked explicitly instead of relying on ad hoc reading of the index.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_template_subfeature_plan_index.md`
- `plan/future_plans/workflow_overhaul/draft/template_subfeature_plans/README.md`
- `plan/future_plans/workflow_overhaul/draft/PLAN_PROGRESS_CHECKLIST.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`

## Scope

- Database: add planning status tracking for template-lineage and generated-task persistence subplans only; no runtime database change.
- CLI: add planning status tracking for generated-task inspection subplans only; no CLI code change.
- Daemon: add planning status tracking for materialization, legality, and drift subplans only; no daemon code change.
- YAML: add planning status tracking for template schema and reference-model subplans only; no YAML runtime change.
- Prompts: add planning status tracking for generated-task objective propagation subplans only; no prompt runtime change.
- Tests: run the task-plan and document-schema verification surface after adding the new progress checklist and updating references.
- Performance: keep the addition as a lightweight planning artifact rather than a second parent queue.
- Notes: add the governing task plan and development log, and update the template subfeature index and draft README to point at the new checklist.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the template subfeature family has a dedicated progress checklist with explicit status values
- the checklist records dependencies between the template subfeature plans
- the template subfeature index and draft README point to the new checklist
- the required development log records the work and verification result
