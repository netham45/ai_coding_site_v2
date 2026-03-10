# Phase F11-S1: Operator Structure And State Commands

## Goal

Implement the operator CLI command family for structure, state, and blockers.

## Rationale

- Rationale: Operators need immediate visibility into tree shape, blockers, dependencies, and current state when diagnosing orchestration behavior.
- Reason for existence: This phase exists to expose the structural and live-state inspection commands that make the rest of the system operable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 is the parent feature for this command family.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 provides the authoritative state these commands inspect.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 supplies blocker and dependency status surfaced here.
- `plan/features/49_F11_operator_history_and_artifact_commands.md`: F11-S2 covers the complementary history and artifact commands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/traceability/action_automation_matrix.md`

## Scope

- Database: create read models for node tree, lineage, state, blockers, and dependencies.
- CLI: implement:
  - node/tree/show commands
  - lineage and relationship inspection
  - blockers and dependency-status commands
  - current run/task/subtask state commands
- Daemon: serve or validate daemon-owned current-state reads where necessary.
- YAML: expose source/resolved structure references cleanly.
- Prompts: no major prompt changes beyond prompt-linked inspection references.
- Tests: exhaustively cover tree rendering, blocker reporting, stale-state handling, and edge-case lineage views.
- Performance: benchmark tree/state/blocker query latency.
- Notes: update introspection notes if additional structure/state views are needed.
