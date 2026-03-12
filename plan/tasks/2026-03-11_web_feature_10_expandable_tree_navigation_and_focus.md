# Task: Web Feature 10 Expandable Tree Navigation And Focus

## Goal

Implement real tree expansion, breadcrumb visibility, and subtree focus in the website sidebar while keeping the existing eager tree payload and current filter set.

## Rationale

- Rationale: The current sidebar still renders the hierarchy as one flat indented list, which does not satisfy the published tree behavior even after multi-root project routing was corrected.
- Reason for existence: This task exists to turn the current tree summary into an actual navigation tool with explicit expansion state and bounded subtree focus.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/10_expandable_tree_navigation_and_focus.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/07_tree_filter_completion.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `notes/planning/implementation/frontend_website_explorer_tree_decisions.md`

## Scope

- Database: no persistence changes are planned; expansion and focus remain browser-local state.
- CLI: no CLI changes are planned; browser hierarchy semantics should still reflect the same tree structure the CLI exposes.
- Daemon: keep the existing full-subtree tree route for this slice unless implementation proves it insufficient.
- Website: add expand/collapse affordances, breadcrumb rendering, subtree focus/reset, and filter behavior over the resulting visible rows.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: update bounded render checks and browser proof for expansion, collapse, ancestor visibility, subtree focus/reset, and filter behavior on collapsed trees.
- Performance: freeze the current loading model explicitly as eager full-subtree fetch plus local expansion/focus state.
- Notes: update the tree implementation note so it records the eager-load decision and no longer overstates the current sidebar behavior.

## Planned Changes

1. Add the governing task plan and development log for feature 10.
2. Implement a browser-local tree state model for expanded node ids and focused subtree root id.
3. Derive selected-node breadcrumb and selected-path expansion from the current route.
4. Replace the flat rendered list with visible rows derived from expansion, focus, and filters.
5. Add bounded UI affordances for:
   - expanding and collapsing one node
   - focusing the selected subtree
   - returning to the full tree
6. Update static render checks, mock browser scenarios, and Playwright tests for the new tree behavior.
7. Update the tree implementation note and feature log with the eager local-expansion decision.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:unit
cd frontend && npx playwright test tests/e2e/tree-filters.spec.js tests/e2e/smoke.spec.js
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the tree renders as an expandable hierarchy rather than one permanently expanded flat list
- the selected node’s ancestor path is visible in the sidebar
- the operator can focus the selected subtree and reset to the full tree
- the required filters still behave correctly over the new visible-row model
- the eager full-subtree loading choice is documented honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
