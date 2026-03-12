# Task: Workflow Overhaul Startup And Create Contract

## Goal

Draft a concrete future-plan contract for profile-aware startup and node creation in the workflow-overhaul bundle, grounded in the current daemon, CLI, and persistence model.

## Rationale

- Rationale: The workflow-overhaul planning work now has enough high-level direction to start freezing concrete contracts, and startup/create is the best first contract because it defines the mutation semantics that later schema, compile, and inspection slices will depend on.
- Reason for existence: This task exists to convert the current future-plan direction for profile-aware startup and creation into a single durable contract note instead of leaving the behavior spread across multiple draft notes.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/cli/handlers.py`
- `src/aicoding/daemon/models.py`

## Scope

- Database: define the version-scoped persistence expectation for selected workflow profile during startup/create.
- CLI: define the intended `workflow start` and `node create` contract changes and what remains out of scope for the first slice.
- Daemon: define request handling, legality checks, title resolution behavior, compile/start behavior, and failure posture.
- YAML: rely on hierarchy and profile applicability rules without reintroducing semantic top-level restrictions.
- Prompts: not directly changed here beyond noting that prompt-stack use happens later at compile/brief time.
- Tests: define the proof expectations the later authoritative implementation slice should satisfy.
- Performance: keep startup response compact and avoid loading full brief/catalog payloads into mutation responses.
- Notes: add the contract note plus required planning/logging artifacts.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a concrete future-plan startup/create contract note exists
- the contract records persistence, legality, request/response, and mutation-scope rules clearly
- the required development log records the reviewed files, commands run, and results
