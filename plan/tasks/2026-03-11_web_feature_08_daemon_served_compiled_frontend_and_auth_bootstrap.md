# Task: Web Feature 08 Daemon-Served Compiled Frontend And Auth Bootstrap

## Goal

Plan the daemon/runtime change that makes the compiled website available directly from the daemon origin on port `8000` and removes the need for manual browser token setup when the website is loaded from that daemon.

## Rationale

- Rationale: The current website runtime requires a separate Vite dev server and manual `localStorage` token injection, which is acceptable for development but not for the normal operator-facing daemon flow.
- Reason for existence: This task exists to define the implementation boundary, proving surface, and packaging implications before any code changes land for daemon-served website runtime.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/08_daemon_served_compiled_frontend_and_auth_bootstrap.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/web/features/06_project_selector_context_and_bootstrap_readiness.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `frontend/README.md`

## Scope

- Database: no direct schema change is planned by default.
- CLI: keep auth-token reporting and operator instructions aligned with the daemon-served website posture.
- Daemon: plan static bundle serving, SPA route fallback, frontend bootstrap/auth injection, and startup failure behavior when compiled assets are absent.
- Website: plan the central bootstrap-consumption change so same-origin daemon loads work without manual token setup while Vite development and test overrides remain possible.
- YAML: not applicable.
- Prompts: not applicable directly.
- Tests: define the canonical integration and browser verification commands for daemon-served website runtime.
- Performance: include first-load/static-delivery and startup-path considerations in the design boundary.
- Notes: record the runtime-vs-dev split and the operator-facing access path explicitly.

## Planned Changes

1. Add the governing web feature plan for daemon-served compiled frontend runtime and auth bootstrap.
2. Define the daemon-side serving model:
   - compiled frontend asset location
   - static-asset mounting
   - SPA fallback routes
   - non-interference with `/api/*`
3. Define the bootstrap/auth model:
   - same-origin `/api` default
   - daemon-provided bearer token for daemon-served loads
   - override precedence for dev/test via env or browser storage
4. Define packaging and install expectations:
   - whether frontend build artifacts are served from the repo checkout, packaged resources, or both
   - what startup/build checks are required to avoid serving a broken website surface
5. Define the proving surface:
   - daemon integration coverage for static HTML, JS assets, SPA fallback, and bootstrap context
   - bounded frontend proof for consuming daemon-served bootstrap
   - real browser proof against `127.0.0.1:8000`
6. Identify the operator/document updates required once implementation lands:
   - daemon startup and website access instructions
   - frontend README runtime split
   - removal of manual browser token setup from the normal getting-started path

## Verification

Canonical verification commands for this planning task:

```bash
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- A new authoritative web feature plan exists for daemon-served compiled frontend runtime and auth bootstrap.
- The plan explicitly covers daemon, website, testing, packaging, and operator-access concerns.
- The task plan is indexed in `plan/tasks/README.md`.
- A development log records the start and completion of the planning work honestly.
- The documented planning verification commands pass.
