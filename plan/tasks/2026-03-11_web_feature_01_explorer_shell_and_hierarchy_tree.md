# Task: Web Feature 01 Explorer Shell And Hierarchy Tree

## Goal

Implement the explorer shell and expanded hierarchy tree for the website, including project bootstrap, root-node auto-selection, expanded tree payloads, and route-synchronized sidebar navigation.

## Rationale

- Rationale: The website now has project selection and top-level creation, but it still lacks the tree-based navigation model that makes node inspection practical.
- Reason for existence: This task exists to make the main website shell usable as an operator explorer instead of a creation-only screen.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`

## Scope

- Database: reuse existing durable tables; do not add new schema unless strictly required.
- CLI: keep tree semantics aligned with operator structure and tree inspection surfaces.
- Daemon: add project bootstrap read model, record project/root linkage durably, and expand the existing tree route.
- Website: render the tree in the persistent shell, support title filtering, show status/rollups, and keep tree selection synchronized with routes.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover project bootstrap, expanded tree payloads, tree filtering, root auto-selection, and route-synced navigation.
- Performance: avoid multi-request tree stitching where one expanded route can serve the sidebar.
- Notes: record the delivered project bootstrap and expanded tree contracts honestly.

## Planned Changes

1. Add the governing task plan and feature log for the explorer/tree slice.
2. Add a project bootstrap read model that resolves the latest top-level root node for a selected website project.
3. Record website project linkage durably when project-scoped top-level creation succeeds.
4. Expand `GET /api/nodes/{node_id}/tree` with version ids, blocker state, child counts, rollups, and timestamps.
5. Add daemon integration and unit coverage for project bootstrap and the expanded tree payload.
6. Replace the shell placeholder sidebar with a real hierarchy tree, title filter, selection highlighting, and route-synced links.
7. Auto-select the root node when visiting `/projects/:projectId` and a root exists.
8. Extend the mock daemon, bounded frontend checks, and Playwright browser proof for tree navigation and filter behavior.
9. Update the implementation notes and future-plan notes to reflect the delivered explorer/tree behavior.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/unit/test_hierarchy.py -q
python3 -m pytest tests/integration/test_node_hierarchy.py tests/integration/test_web_explorer_tree_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the daemon exposes a project bootstrap read model that can resolve the current root node for a project
- project-scoped top-level creation records project/root linkage durably
- the existing tree route returns the expanded browser contract
- the shell renders a real hierarchy tree with route-synced selection and title filtering
- `/projects/:projectId` auto-selects the root node when one exists
- the project/tree contracts are documented honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
