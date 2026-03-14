# Task: Workflow Overhaul Unified Command Lifecycle Planning

## Goal

Add the unified command lifecycle proposal to the workflow-overhaul notes and create one draft plan per built-in subtask command so the migration is governed as full-scope work rather than an ad hoc refactor.

## Rationale

- Rationale: The current command semantics are split across YAML families, compiled subtask handling, daemon mutation paths, and intervention/action surfaces, which makes lifecycle truth and blocked/completed behavior harder to reason about than it should be.
- Reason for existence: This task exists to turn the unified command lifecycle idea into an explicit workflow-overhaul note and a complete draft plan inventory covering every built-in subtask command instead of leaving the idea as a partial or convenience migration.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_templated_task_generation_overview.md`

## Scope

- Database: record the planned durable state expectations for unified command lifecycle handling and action/result truth, without changing runtime persistence code in this planning pass.
- CLI: capture the command/action surfaces that will need to align with a unified lifecycle contract, including daemon-backed mutations and recommended-action reads.
- Daemon: define the planned handler/lifecycle contract and inventory all command kinds and adjacent action surfaces that must move onto it.
- YAML: inventory the built-in task and subtask YAML assets that would need schema and compile alignment to the unified contract.
- Prompts: capture the prompt-bearing command kinds that will need standardized lifecycle/result semantics.
- Tests: run the task-plan and document-schema verification surface after adding the new notes and draft-plan family.
- Performance: keep the change at the planning layer; do not widen into runtime implementation in this pass.
- Notes: add the command-lifecycle future-plan note bundle, the draft feature slice, the command subfeature index/README, the per-command draft plans, and the development log.

## Documentation Impact

- Status: reviewed_no_change
- Affected documentation surfaces:
  - `docs/README.md`
- Rationale: this task governs workflow-overhaul planning and draft-plan inventory work, but it does not directly revise current user-facing or operator-facing documentation content.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_user_documentation_governance_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul notes contain the unified command lifecycle proposal with a full inventory of in-scope command and action surfaces
- the draft feature-plan family includes a dedicated unified-command-lifecycle slice
- the draft plan tree contains one plan file for each built-in subtask command
- the draft README and index surfaces reference the new command subfeature family
- the required development log records the work and verification result
