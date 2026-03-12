# Task: Workflow Overhaul Code Alignment And Plan Coverage Audit

## Goal

Audit the executable workflow-overhaul draft plans against the current code, add relevant current-code references to those plans, and identify future-plan note coverage gaps.

## Rationale

- Rationale: The executable draft plans currently describe target work, but they do not point clearly enough at the current code that will need to change.
- Reason for existence: This task exists to anchor the draft queue to the real codebase and to surface which future-plan notes still lack dedicated execution-plan coverage.

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
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`

## Scope

- Database: inspect current persistence surfaces that the draft plans would touch and record them in the plans.
- CLI: inspect current CLI handlers and parser surfaces that the draft plans would touch and record them in the plans.
- Daemon: inspect current compile, startup, materialization, and orchestration code that the draft plans would touch and record them in the plans.
- YAML: inspect current schema and builtin YAML loading surfaces that the draft plans would touch and record them in the plans.
- Prompts: inspect current prompt-reference and prompt-pack surfaces that the draft plans would touch and record them in the plans.
- Tests: run the task-plan and document-schema verification surface after updating the draft plans and coverage notes.
- Performance: not applicable for this audit pass.
- Notes: update the executable draft plans with code references and current gaps, add a coverage-audit note, and record the work in the development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the executable draft setup and feature plans include relevant current-code references
- the executable draft setup and feature plans record the current runtime/coverage gaps that matter to implementation ordering
- the draft plan index records which future-plan notes are still only supporting inputs or still missing dedicated execution-plan coverage
- the required development log records the audit and verification result
