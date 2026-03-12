# Task: Web Feature 09 Project Multi-Root Navigation And Creation Persistence

## Goal

Implement project-scoped multi-root navigation and keep top-level creation accessible even after one or more top-level nodes already exist for the selected project.

## Rationale

- Rationale: The current website collapses each project to one latest-root redirect, which hides existing top-level nodes and blocks operators from returning to the creation surface.
- Reason for existence: This task exists to align the project route, project bootstrap read model, and sidebar behavior with the real multi-root behavior allowed by the daemon.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/09_project_multi_root_navigation_and_creation_persistence.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `notes/planning/implementation/frontend_website_explorer_tree_decisions.md`

## Scope

- Database: reuse current workflow-event linkage for project-owned top-level nodes unless implementation proves a stronger durable project-root index is required.
- CLI: no CLI changes are planned; browser multi-root behavior must remain semantically consistent with existing top-level workflow creation.
- Daemon: extend the project bootstrap response so it can describe multiple project-owned top-level nodes and a recommended route hint.
- Website: stop redirecting `/projects/:projectId` away from the project workspace, render existing top-level nodes explicitly, and anchor the sidebar to the correct top-level root for the selected node route.
- YAML: not applicable.
- Prompts: preserve existing top-level prompt/title entry semantics while allowing repeated root creation.
- Tests: add daemon integration coverage for multi-root bootstrap payloads and browser proof that the project route stays usable after a root already exists.
- Performance: keep project bootstrap and selected-root lookup lightweight.
- Notes: update the explorer-tree implementation note because its current auto-redirect decision is no longer correct.

## Planned Changes

1. Add the governing task plan and development log for feature 09.
2. Extend `GET /api/projects/{project_id}/bootstrap` with a top-level node catalog while preserving a recommended route hint.
3. Stop redirecting the project route when roots already exist.
4. Render an existing-top-level-node section on the project page alongside the creation form.
5. Use the selected node’s ancestor chain to choose the correct root tree in the sidebar when viewing a node under a non-latest top-level root.
6. Update mock-daemon scenarios and Playwright coverage so they no longer encode the single-root redirect behavior.
7. Update the implementation note and feature log with the corrected multi-root behavior.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_web_explorer_tree_api.py tests/integration/test_web_project_bootstrap_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run test:e2e -- --grep "project selection|project selector|project workspace|multi-root"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `/api/projects/{project_id}/bootstrap` can describe more than one top-level node for a project
- `/projects/:projectId` remains a usable project workspace when roots already exist
- the website still allows creating another top-level node for the selected project
- the sidebar tree follows the selected node’s actual top-level root instead of always using the latest project root
- integration and browser proof cover multi-root project behavior honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
