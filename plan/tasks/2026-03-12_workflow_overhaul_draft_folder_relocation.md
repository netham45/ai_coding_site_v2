# Task: Workflow Overhaul Draft Folder Relocation

## Goal

Move only the executable workflow-overhaul implementation-plan assets into `plan/future_plans/workflow_overhaul/draft/` and keep the supporting notes at the top level.

## Rationale

- Rationale: The workflow-overhaul future-plan bundle currently mixes executable implementation plans with supporting notes and examples.
- Reason for existence: This task exists to isolate the step-by-step implementation plans under a clear `draft/` folder without burying the supporting notes, prompts, schemas, and examples.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`

## Scope

- Database: not applicable for this note relocation.
- CLI: not applicable for runtime behavior, but update CLI-facing plan references if they point into the moved folder.
- Daemon: not applicable for runtime behavior, but update daemon-facing plan references if they point into the moved folder.
- YAML: update future-plan YAML example references if they point into the moved folder.
- Prompts: update future-plan prompt-bundle references if they point into the moved folder.
- Website: not applicable for runtime behavior, but update web-plan references if they point into the moved folder.
- Tests: run the task-plan and document-schema verification surface after the relocation.
- Performance: not applicable.
- Notes: add a relocation task, development log, and update path references that become stale.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a new `plan/future_plans/workflow_overhaul/draft/` directory exists
- only the executable workflow-overhaul implementation-plan assets live under that directory
- supporting workflow-overhaul notes, prompts, schemas, examples, and draft inputs remain at the top level
- stale in-repo references are updated for the moved and restored scope
- the required development log records the relocation and verification result
