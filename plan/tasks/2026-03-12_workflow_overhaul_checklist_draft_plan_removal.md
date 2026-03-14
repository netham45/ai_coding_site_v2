# Task: Workflow Overhaul Checklist Draft Plan Removal

## Goal

Remove the obsolete checklist draft-plan families from the workflow-overhaul draft tree now that templated task generation is the active replacement direction.

## Rationale

- Rationale: The draft tree still contained checklist draft feature plans, checklist subfeature plans, and checklist future-flow drafts even after the plan direction had moved to template-driven task generation.
- Reason for existence: This task exists to delete the obsolete checklist draft-plan files so the remaining workflow-overhaul queue reflects only the active planning model.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_templated_task_generation_overview.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_templated_task_generation_feature_breakdown.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`

## Scope

- Database: no database behavior changes; this task only removes obsolete planning artifacts and updates the draft indexes that describe future database-facing work.
- CLI: no CLI behavior changes; update draft-plan references so CLI-facing future work points only at the template-generation direction.
- Daemon: no daemon behavior changes; update draft-plan references so daemon-facing future work points only at the template-generation direction.
- YAML: remove checklist draft-plan files that no longer represent the preferred YAML and compile direction.
- Prompts: remove checklist prompt-alignment draft plans and leave the generated-task objective contract as the active prompt direction.
- Tests: run the task-plan and document-schema verification surface after deleting the obsolete draft-plan families and updating the indexes.
- Performance: keep the cleanup doc-only and avoid widening the change into runtime refactors.
- Notes: add the governing task plan and development log, and update the draft README and progress checklist to reflect the slimmer active queue.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the obsolete checklist draft feature-plan files are deleted
- the obsolete checklist subfeature-plan files are deleted
- the obsolete checklist future-flow drafts are deleted
- the workflow-overhaul draft README, index, and progress checklist reference only the active template-generation draft-plan family
- the required development log records the cleanup and verification result
