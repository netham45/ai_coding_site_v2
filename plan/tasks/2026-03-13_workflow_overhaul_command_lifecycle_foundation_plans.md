# Task: Workflow Overhaul Command Lifecycle Foundation Plans

## Goal

Add the missing foundation draft plans for the unified command lifecycle family so the per-command plans inherit from an explicit shared interface, shared state/result model, shared registry/dispatch path, and shared YAML-to-operator projection contract.

## Rationale

- Rationale: One file per command kind is not enough if the repo does not also plan the abstract handler shape those command plans are supposed to share.
- Reason for existence: This task exists to prevent the new command draft family from implying twenty-three bespoke migrations without an explicit plan for the common lifecycle contract they all depend on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-13_unified_command_lifecycle_contract.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

## Scope

- Database: capture the planned durable state/result model dependencies for command handlers without changing runtime persistence code in this planning pass.
- CLI: add draft-plan coverage for command status projection, legality rendering, and action execution surfaces.
- Daemon: add draft-plan coverage for the abstract command handler interface and the registry/dispatch path that command kinds will share.
- YAML: add draft-plan coverage for the declarative command-definition boundary and compile-time alignment expectations.
- Prompts: capture the shared command contract implications for prompt-bearing commands and result-projection surfaces.
- Website UI: add draft-plan coverage for daemon-provided status, blocked-reason, and next-action projection rather than ad hoc browser logic.
- Tests: run the task-plan and document-schema verification surface after the draft-plan family changes.
- Performance: keep this batch at the planning/document layer; do not widen into runtime performance changes in this pass.
- Notes: update the unified command lifecycle note and draft indexes/readmes to reflect the new foundation-plan layer.

## Documentation Impact

- Status: reviewed_no_change
- Affected documentation surfaces:
  - `docs/README.md`
- Rationale: this task adds workflow-overhaul planning notes and draft plans but does not directly change current user-facing or operator-facing runtime documentation surfaces.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_user_documentation_governance_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the unified command lifecycle note explicitly states the required shared foundation layer
- the command subfeature draft family includes dedicated foundation plans for the interface, shared models, registry/dispatch, and YAML/operator projection
- the command subfeature index and README describe the foundation plans as prerequisites for the per-command plans
- the task-plan README and development log reflect the new planning batch
- the document consistency tests pass after the changes
