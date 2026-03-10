# Phase F14: Optional Pushed Child Sessions

## Goal

Support bounded child sessions for research, review, and verification without transferring node ownership.

## Rationale

- Rationale: Some work benefits from isolated research or review sessions, but ownership of the parent node still has to remain clear and durable.
- Reason for existence: This phase exists to support bounded delegation without turning every child session into an uncontrolled fork of orchestration state.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 provides the parent CLI interaction model child sessions must not bypass.
- `plan/features/16_F12_session_binding_and_resume.md`: F12 governs how child sessions are bound and tracked safely.
- `plan/features/20_F15_child_node_spawning.md`: F15 is the node-owning alternative to pushed child sessions.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 covers merge-back style reconciliation that is conceptually adjacent.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: child session records, parent linkage, merge-back payloads.
- CLI: push/pop/show child-session commands.
- Daemon: bounded delegation, session launch, merge-back validation.
- YAML: declarative child-session subtask patterns.
- Prompts: delegated research/review/verification prompts.
- Tests: exhaustive push, merge-back, invalid return, and parent-cursor ownership coverage.
- Performance: benchmark child-session launch and merge-back overhead.
- Notes: update child-session contract notes if payload shape changes.
