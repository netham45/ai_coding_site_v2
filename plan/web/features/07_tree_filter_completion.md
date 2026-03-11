# Web Feature 07: Tree Filter Completion

## Goal

Complete the remaining required v1 tree filters so the explorer shell supports the agreed operator filtering behavior rather than only a local title search.

## Rationale

- Rationale: The current explorer shell has a usable tree and route synchronization, but it only implements local title filtering while the v1 scope required lifecycle, blocked-only, active-only, and kind filtering.
- Reason for existence: This phase exists to close the remaining tree-navigation gap so operators can narrow large hierarchies by runtime state instead of scanning visually.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `notes/planning/implementation/frontend_website_explorer_tree_decisions.md`

## Scope

- Database: no direct schema work is expected unless filterable fields prove to be missing from the expanded tree payload.
- CLI: keep state/filter semantics aligned with existing operator state vocabulary.
- Daemon: extend the tree read surface only if current expanded tree fields are still insufficient to support the required filters efficiently.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover lifecycle, blocked-only, active-only, and kind filter behavior in bounded and browser proof.
- Performance: filtering should not force a costly full-detail reload path for every change.
- Notes: update tree and routing notes to reflect the actual filter model and any query-param or local-state decisions.

## Planned Work

1. Confirm the expanded tree payload includes enough state to support:
   - lifecycle filter
   - blocked-only filter
   - active-only filter
   - kind filter
2. Decide and document whether each filter is purely client-side over the loaded tree payload or requires daemon-assisted query support.
3. Implement a coherent filter UI in the explorer shell instead of one-off controls.
4. Preserve selection and route behavior while filters change.
5. Add daemon tests if the read contract expands, plus bounded frontend and Playwright proof for the full agreed filter set.
