# Task: Refresh The Getting Started Guide

## Goal

Refresh the getting-started walkthrough so it guides a new operator through the actual current bootstrap, daemon startup, first workflow start, and inspection surfaces implemented in this repository.

## Rationale

- Rationale: The repository already has a getting-started walkthrough, but the live CLI, daemon, session, and verification surfaces have evolved enough that the guide needs to be tightened against the current implementation and notes.
- Reason for existence: This task exists to keep the onboarding guide aligned with the real program and doctrinal notes instead of leaving a partially hypothetical walkthrough to drift past the code.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`: the guide needs to reflect the actual top-level `workflow start` path and its current constraints.
- `plan/features/15_F11_operator_cli_and_introspection.md`: the guide needs to emphasize the current inspection-first operator surfaces.
- `plan/features/13_F09_node_run_orchestration.md`: the guide needs to describe how run progress and `workflow advance` fit together today.
- `plan/features/16_F12_session_binding_and_resume.md`: the guide needs to explain when `session bind`, `session show-current`, and recovery surfaces are relevant.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: not applicable for this documentation task, but the guide must describe the real database bootstrap commands and schema expectations that the daemon and CLI rely on.
- CLI: update the guide so the documented bootstrap, workflow-start, inspection, and session commands match the live parser and current tests.
- Daemon: update the guide so daemon startup, token-file behavior, and health/inspection expectations match the current FastAPI app and config posture.
- YAML: not applicable for implementation in this task, but the guide should explain the built-in node hierarchy and the compile-time YAML inspection surfaces a first-time operator is likely to use.
- Prompts: not applicable for implementation in this task, but the guide should explain how `subtask prompt`, `subtask context`, prompt history, and prompt-pack inspection fit into first-run inspection.
- Tests: run the authoritative documentation tests that cover task plans, document schema, and quickstart docs after the guide refresh.
- Performance: negligible for this task.
- Notes: refresh the walkthrough, fix any adjacent command drift discovered in README/task indexes, and keep the development log current.

## Verification

- Documentation checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py -q`

## Exit Criteria

- The getting-started walkthrough explains how to bootstrap the database, start the daemon, run a first workflow, and inspect the resulting state using the current CLI surfaces.
- The walkthrough distinguishes currently proven behavior from still-partial or environment-gated surfaces.
- Any adjacent authoritative command drift discovered during the refresh is corrected in the same change.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log exists, cites this task plan, and records both the start and completion state.
- The documented verification command passes.
