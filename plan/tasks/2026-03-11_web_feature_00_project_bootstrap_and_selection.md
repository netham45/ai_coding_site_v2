# Task: Web Feature 00 Project Bootstrap And Selection

## Goal

Implement the first authoritative website feature phase by replacing the placeholder projects route with real daemon-backed project discovery, project selection, and top-level node creation behavior.

## Rationale

- Rationale: The website setup scaffold is complete, but it still cannot establish a real operator project context or start a top-level workflow through the browser.
- Reason for existence: This task exists to make project bootstrap and top-level creation the first real browser-backed operator flow before tree and detail features land.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`

## Scope

- Database: no direct schema change is planned in this slice.
- CLI: keep top-level creation semantics aligned with the existing workflow-start behavior.
- Daemon: add project catalog and project-scoped top-level creation HTTP surfaces.
- Website: implement project discovery, project selection, and the inline-confirmed top-level creation form.
- YAML: not applicable; no YAML schema or policy change is planned in this slice.
- Prompts: support operator-entered top-level prompt input without extra prompt-content validation.
- Tests: add daemon integration coverage, bounded frontend proof, and browser E2E coverage for project selection and creation.
- Performance: keep project discovery and creation responsive at normal operator scale.
- Notes: record the actual delivered browser contract, including the current limitation that repo-backed top-level bootstrap still remains deferred behind later live-git work.

## Planned Changes

1. Add the governing task plan and development log for this feature slice.
2. Add daemon models and helper logic for a project catalog rooted at `workspace_root / "repos"` and a project-scoped top-level creation response.
3. Add daemon routes for `GET /api/projects` and `POST /api/projects/{project_id}/top-level-nodes`.
4. Add daemon integration tests for project listing, empty project catalog behavior, invalid project rejection, and successful top-level creation through the new route.
5. Replace the placeholder projects and project-detail pages with a real project-selection and top-level creation flow using Axios and TanStack Query.
6. Extend the mock-daemon harness, bounded frontend checks, and Playwright browser tests to cover the first real browser-backed operator flow.
7. Update the implementation note and future-plan note to reflect the actual shipped contract and the remaining repo-bootstrap gap honestly.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/integration/test_web_project_bootstrap_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `GET /api/projects` returns the daemon-managed website project catalog rooted under `repos/`.
- `POST /api/projects/{project_id}/top-level-nodes` creates a top-level workflow through the existing workflow-start semantics and returns website navigation metadata.
- The website renders real project discovery and top-level creation instead of placeholder copy.
- The top-level creation flow uses inline confirmation with `create node` and `keep editing`.
- The delivered browser contract and remaining repo-bootstrap limitation are documented honestly.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
