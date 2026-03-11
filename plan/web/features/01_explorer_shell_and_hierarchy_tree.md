# Web Feature 01: Explorer Shell And Hierarchy Tree

## Goal

Implement the explorer shell and expanded hierarchy tree contract.

## Rationale

- Rationale: The tree and shell are the main operator navigation surfaces.
- Reason for existence: This feature exists to make hierarchy navigation, selection, rollups, and route synchronization inspectable and testable through one coherent browser shell.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
- `AGENTS.md`

## Scope

- Database: not expected directly unless new tree-summary fields require persistence changes.
- CLI: keep tree semantics aligned with operator-structure surfaces.
- Daemon: expand the existing tree route and support shell-facing read models.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover expanded tree payloads, tree rendering, filters, selection, and route sync.
- Performance: tree loading and refresh should stay practical for larger hierarchies.
- Notes: keep tree contract and routing notes synchronized with implementation.
