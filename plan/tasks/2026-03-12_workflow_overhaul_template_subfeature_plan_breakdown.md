# Task: Workflow Overhaul Template Subfeature Plan Breakdown

## Goal

Expand the template-generation draft feature family into file-per-child subfeature plans so it matches the granularity of the workflow-profile side.

## Rationale

- Rationale: The active template-generation direction has top-level draft feature plans, but it still lacks the deeper one-file-per-child breakdown that made the earlier checklist draft feel more operationally decomposable.
- Reason for existence: This task exists to add the missing template subfeature plan family, index, and README so the active queue preserves the same ultra-granular planning protocol.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_templated_task_generation_feature_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_task_sequence_template_schema_draft.md`
- `plan/future_plans/workflow_overhaul/draft/README.md`
- `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`

## Scope

- Database: add granular planning slices for template provenance and generated-task lineage persistence without changing runtime code.
- CLI: add granular planning slices for generated-task inspection and template-provenance read surfaces.
- Daemon: add granular planning slices for materialization, dependency freeze, recompile drift, and runtime legality.
- YAML: add granular planning slices for task-sequence schema, template definition, and cross-reference validation.
- Prompts: add granular planning slices for generated-task objective propagation and prompt-context alignment.
- Tests: run the task-plan and document-schema verification surface after adding the new subfeature plan family and updating the draft indexes.
- Performance: keep the new child plans concise and implementation-sized rather than turning them into another prose bundle.
- Notes: add the new subfeature directory, index, README, governing task plan, and development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the template-generation family has a dedicated subfeature-plan directory with file-per-child assets
- the draft README and draft index explain how the new template subfeature plans relate to the active feature queue
- the new subfeature index maps the child plans back to their parent template-generation feature slices
- the required development log records the work and verification result
