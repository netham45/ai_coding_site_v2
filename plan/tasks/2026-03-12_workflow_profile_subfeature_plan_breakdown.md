# Task: Workflow Profile Subfeature Plan Breakdown

## Goal

Break the broad workflow-profile draft feature plans into deeper implementation-sized subfeature plans with one file per child plan.

## Rationale

- Rationale: The broad workflow-profile draft feature plans still grouped too much behavior per slice and were not yet broken down far enough for real implementation sequencing.
- Reason for existence: This task exists to replace grouped parent notes with 50 standalone child-plan files across 10 broad areas.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/07_profile_e2e_and_traceability.md`

## Scope

- Database: the deeper breakdown should isolate persistence-heavy profile slices.
- CLI: the deeper breakdown should isolate read-surface and startup-surface slices.
- Daemon: the deeper breakdown should isolate compile, materialization, enforcement, and read-surface slices.
- YAML: the deeper breakdown should isolate schema, node-definition, and layout-definition slices.
- Prompts: the deeper breakdown should isolate brief-generation and prompt-stack work where applicable.
- Tests: run the task-plan and document-schema verification surface after adding the new planning artifacts.
- Performance: keep the subfeature plans implementation-sized and concise.
- Notes: add the workflow-profile subfeature-plan family, index note, and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-profile family has a deeper subfeature-plan directory
- each broad workflow-profile area is broken into 5 standalone child-plan files
- the required development log records the work and verification result
