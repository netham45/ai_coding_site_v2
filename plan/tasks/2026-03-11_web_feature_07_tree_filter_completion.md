# Task: Web Feature 07 Tree Filter Completion

## Goal

Implement the remaining required v1 explorer-tree filters so the website supports lifecycle, blocked-only, active-only, and kind filtering instead of only local title search.

## Rationale

- Rationale: The explorer shell already has the expanded tree payload and route-aware navigation, but the current sidebar leaves large hierarchies hard to inspect because only a title filter exists.
- Reason for existence: This task exists to close the remaining v1 tree-navigation gap using the state already exposed by the expanded tree contract.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/07_tree_filter_completion.md`
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

- Database: no direct schema work is expected.
- CLI: keep filter vocabulary aligned with existing lifecycle and operator-state naming.
- Daemon: reuse the current expanded tree route unless implementation proves a missing field.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover lifecycle, blocked-only, active-only, kind, and text filtering in bounded and browser proof.
- Performance: filters should remain client-side over the loaded tree payload and avoid triggering fresh tree fetches for every control change.
- Notes: update the explorer-tree implementation note and future-plan scope note so they reflect the shipped filter model honestly.

## Planned Changes

1. Add this governing task plan and the paired development log for feature 07.
2. Confirm the existing expanded tree payload is sufficient for lifecycle, blocked-only, active-only, and kind filtering without further daemon contract changes.
3. Replace the one-off title filter input with a coherent filter panel in the sidebar.
4. Keep route selection stable while filters change, including the case where the selected node is currently filtered out of the visible list.
5. Add bounded frontend proof for the full filter panel and Playwright browser coverage for the agreed v1 filter set.
6. Update the explorer-tree implementation note and the v1 scope note to reflect the completed filter surface.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- The explorer sidebar supports lifecycle, blocked-only, active-only, kind, and text filtering together.
- Filter changes do not require daemon-side refetch beyond the existing tree polling behavior.
- The selected node route remains stable while filters change.
- Bounded proof and browser proof exist for the shipped filter set.
- The implementation note and future-plan scope note are updated honestly.
- The governing task plan and development log reference each other.
