# Task: Workflow Overhaul Missing Gap Plan Additions

## Goal

Add the missing executable workflow-overhaul draft plans for workflow-profile website UI support and profile/checklist migration-backfill work.

## Rationale

- Rationale: The draft execution queue still had identified coverage gaps after the code-alignment audit.
- Reason for existence: This task exists to close those planning gaps so the primary draft queue covers the missing implementation areas explicitly.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_web_ui_integration_plan.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`

## Scope

- Database: add a dedicated draft plan for migration/backfill posture around new profile and checklist persistence.
- CLI: reflect queue changes in the draft execution docs and checklist where CLI/operator sequencing depends on the new plans.
- Daemon: reflect queue changes in the draft execution docs and checklist where daemon sequencing depends on the new plans.
- YAML: not applicable for direct runtime behavior, but the new plans should reference the relevant schema and persistence surfaces.
- Prompts: not applicable for direct runtime behavior, but the website-support plan should note prompt-backed profile/brief surfaces.
- Tests: run the task-plan and document-schema verification surface after adding the plans and updating the queue docs.
- Performance: not applicable.
- Notes: add the missing draft feature plans, update the draft indexes/README/checklist, and record the work in the development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the draft feature-plan family includes a workflow-profile website UI support slice
- the draft feature-plan family includes a migration/backfill slice for profile/checklist persistence
- the draft queue docs and progress checklist include the new plans in the right order
- the required development log records the change and verification result
