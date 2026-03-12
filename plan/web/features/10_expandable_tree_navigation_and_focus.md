# Web Feature 10: Expandable Tree Navigation And Focus

## Goal

Replace the current flattened indented list with a real hierarchy explorer that supports expand/collapse, ancestor visibility, and subtree focus.

## Rationale

- Rationale: The current sidebar renders every node in one filtered list and never exposes actual expansion state, breadcrumb context, or subtree focus, which falls short of the published tree behavior.
- Reason for existence: This feature exists to make the website tree behave like an operator navigation tool rather than a static flattened report.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/07_tree_filter_completion.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `AGENTS.md`

## Scope

- Database: reuse current hierarchy and lifecycle records; no new persistence is expected unless expansion state becomes daemon-owned.
- CLI: keep node identity, hierarchy, and blocker semantics aligned with operator structure views.
- Daemon: confirm whether the existing full-subtree route is sufficient or whether a children-on-demand read model is needed for practical lazy expansion.
- Website: add expansion state, collapse behavior, ancestor/breadcrumb display, explicit subtree focus, and route-synchronized selected-node visibility.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover expand/collapse, preserving selection under collapse, ancestor path visibility, subtree focus/reset, and filter behavior over collapsed and expanded states.
- Performance: avoid forcing the browser to render or diff large full trees unnecessarily; document whether v1 remains eager-load or moves to lazy child fetches.
- Notes: update the website tree notes if implementation freezes a different loading model than the current exploratory note.

## Planned Work

1. Define the frontend tree state model explicitly:
   - expanded node ids
   - selected node id
   - focused subtree root id when used
   - derived visible rows
2. Add real expand/collapse affordances that use `has_children` and `child_count` rather than always rendering every node.
3. Add ancestor-path or breadcrumb rendering for the current selection.
4. Add a bounded subtree-focus action that narrows the visible tree to one branch and supports returning to the full tree.
5. Decide whether v1 remains:
   - eager full-subtree fetch with local expansion
   - or lazy child expansion backed by daemon reads
6. Extend mock data and browser tests to cover deep trees, collapsed trees, and focused-subtree navigation.

## Notes

- The current required filters remain part of the tree contract, but they are not sufficient to satisfy the published tree behavior on their own.
- If lazy loading is adopted, the future-plan note for tree loading must be updated in the same implementation batch.
