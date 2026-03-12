# Task: Workflow Overhaul Remaining Gap Slice Additions

## Goal

Add standalone draft feature plans for the remaining workflow-overhaul support-note gaps so the draft folder contains explicit executable slices instead of indirect-only coverage.

## Rationale

- Rationale: The draft execution queue still listed multiple support-note topics as indirectly covered rather than broken into standalone execution slices.
- Reason for existence: This task exists to convert those remaining gaps into actual numbered draft plans in the `draft/` folder and wire them into the queue order.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_pydantic_model_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_helper_assembly_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_execution_mode_overview.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_execution_mode_flow_impact.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_execution_mode_proposed_note_and_code_updates.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_checklist_item_prompt_contract.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_e2e_task_profile_catalog.md`

## Scope

- Database: capture the remaining draft-plan slices that affect persistence models, migration posture, and typed runtime contracts.
- CLI: update the queue docs and plan slices where command and inspection surface work is part of the newly added coverage.
- Daemon: update the queue docs and plan slices where route, helper, response-shape, and legality work is part of the added coverage.
- YAML: capture the draft slices that depend on typed schema and workflow-profile asset structure.
- Prompts: add the missing prompt-alignment slice for checklist prompt assets.
- Website: capture the missing response-shape and route-consumer slices where browser surfaces depend on them.
- Tests: run the authoritative task-plan and document-schema verification surface after adding the plans and queue updates.
- Performance: not applicable for direct runtime behavior.
- Notes: add the remaining draft feature plans, update the draft queue docs and checklist, and record the work in the development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the remaining indirectly covered support-note topics each have a standalone executable draft feature plan where appropriate
- the draft queue docs and progress checklist include the new plans in execution order
- the draft index no longer describes those topics as uncovered gaps
- the required development log records the change and verification result
