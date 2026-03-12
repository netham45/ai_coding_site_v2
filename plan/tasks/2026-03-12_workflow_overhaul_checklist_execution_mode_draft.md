# Task: Workflow Overhaul Checklist Execution Mode Draft

## Goal

Draft the checklist execution-mode schema, checklist-item prompt contract, and example instance for the workflow-overhaul bundle.

## Rationale

- Rationale: The workflow-overhaul direction needs a structured way to execute multi-step task work one item at a time without inventing a separate semantic task type.
- Reason for existence: This task exists to turn the checklist idea into an explicit future-plan contract with a schema, prompt contract, and example instance.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_prompt_contract.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`

## Scope

- Database: draft the durable checklist instance and blocker shape the runtime would need to persist.
- CLI: draft the orchestrator-facing checklist execution assumptions without defining final commands yet.
- Daemon: draft the execution-mode contract, status vocabulary, blocker shape, and trust boundary.
- YAML: define checklist schema and template shapes as future declarative assets.
- Prompts: define the active checklist-item prompt contract, including `When To Use This`.
- Tests: run the task-plan and document-schema verification surface after adding the new notes.
- Performance: keep the checklist schema constrained and sequential by default.
- Notes: add the schema draft, prompt contract, example instance, and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul bundle has a checklist execution-mode schema draft
- the bundle has a checklist-item prompt contract with `When To Use This`
- the bundle has a concrete example checklist instance
- the required development log records the work and verification result
