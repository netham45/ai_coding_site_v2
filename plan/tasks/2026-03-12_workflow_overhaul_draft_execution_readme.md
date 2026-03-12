# Task: Workflow Overhaul Draft Execution README

## Goal

Add a `draft/README.md` that explains which workflow-overhaul draft assets are the executable implementation plans, what order to execute them in, and how the supporting breakdown files fit around that queue.

## Rationale

- Rationale: The `workflow_overhaul/draft/` subtree now contains both the primary execution queue and supporting breakdown assets, which makes the intended order easy to misread.
- Reason for existence: This task exists to make the draft folder operationally understandable before anyone starts turning these draft plans into real `plan/` execution work.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_workflow_profile_subfeature_plan_index.md`

## Scope

- Database: not applicable for runtime behavior, but the README should reflect when DB-heavy slices occur in the execution order.
- CLI: not applicable for runtime behavior, but the README should describe when CLI/operator slices are expected to land.
- Daemon: not applicable for runtime behavior, but the README should describe the main implementation sequence around runtime authority.
- YAML: the README should make clear when YAML/schema work comes before runtime work.
- Prompts: the README should make clear that prompt adoption is downstream of core profile/runtime freezes.
- Tests: run the task-plan and document-schema verification surface after adding the README and any related index updates.
- Performance: not applicable.
- Notes: add the README, align the draft index note if needed, and record the work in the development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `plan/future_plans/workflow_overhaul/draft/README.md` exists
- the README explicitly distinguishes the primary execution queue from supporting breakdown assets
- the README gives a recommended execution order for the draft plans
- the README explains whether checklist-mode work should be mixed into the workflow-profile queue or handled as a later wave
- the required development log records the change and verification result
