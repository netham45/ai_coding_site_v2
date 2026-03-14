# Task: Workflow Overhaul Template Support Draft Plan Alignment

## Goal

Update the remaining workflow-overhaul draft plans so template support is reflected consistently across the ultra-granular setup, proving, and reconciliation slices.

## Rationale

- Rationale: The active draft queue already uses templated task generation, but several setup and cross-cutting draft plans still describe the earlier checklist-runtime model.
- Reason for existence: This task exists to align the remaining draft plans with the active template-generation direction so downstream implementation work does not inherit stale assumptions.

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
- `plan/future_plans/workflow_overhaul/2026-03-12_task_sequence_template_schema_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_templated_task_generation_feature_breakdown.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`

## Scope

- Database: update draft-plan language where persistence readiness now concerns template references and generated-task lineage instead of checklist-instance state.
- CLI: update draft-plan language where CLI/operator surfaces now concern template provenance and generated-task inspection.
- Daemon: update draft-plan language where runtime posture now concerns template-driven child materialization rather than checklist-mode execution.
- YAML: update draft-plan language where schema readiness now concerns task-sequence templates and template example assets.
- Prompts: update draft-plan language where prompt readiness now concerns generated-task objective context rather than checklist-item prompts.
- Tests: run the task-plan and document-schema verification surface after the draft-plan alignment edits.
- Performance: keep the change scoped to draft-plan alignment rather than widening into runtime design edits beyond the already-adopted direction.
- Notes: add the governing task plan and development log, and patch the affected draft setup and feature plans so template support is explicit.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul draft setup plans explicitly describe template support where applicable
- the cross-cutting draft feature plans explicitly describe template support where applicable
- stale checklist-runtime phrasing is removed from the active granular draft queue except where historical context is intentional
- the required development log records the alignment work and verification result
