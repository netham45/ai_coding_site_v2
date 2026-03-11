# Task: Web Feature 08 Daemon-Served Compiled Frontend And Auth Bootstrap Implementation

## Goal

Implement the daemon-served compiled website runtime so the daemon can serve the built frontend on port `8000` and provide the frontend auth/bootstrap context automatically for same-origin loads.

## Rationale

- Rationale: The planning phase is complete, and the current runtime still requires a separate Vite dev server plus manual browser token setup for ordinary use.
- Reason for existence: This task exists to execute the feature plan in a scoped implementation pass with bounded proof for daemon-side serving, frontend bootstrap consumption, and missing-build behavior.

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
- `frontend/README.md`

## Scope

- Database: no direct schema work is planned.
- CLI: no CLI surface change beyond keeping token and website access posture aligned with existing daemon behavior.
- Daemon: add compiled frontend serving, static asset delivery, SPA fallback, and injected same-origin bootstrap/auth context.
- Website: consume daemon-served bootstrap context through the central API client while preserving dev/test override paths.
- YAML: not applicable.
- Prompts: not applicable directly.
- Tests: add bounded integration coverage for daemon-served runtime and update frontend bounded checks for bootstrap precedence.
- Performance: keep index/bootstrap rendering and static asset serving lightweight.
- Notes: update runtime-facing frontend notes to describe the normal daemon-served path versus Vite development.

## Planned Changes

1. Add the governing implementation task plan and paired development log.
2. Add a daemon-side frontend runtime helper for:
   - locating the compiled frontend bundle
   - serving built assets
   - injecting same-origin bootstrap/auth context into the HTML shell
   - returning a clear failure when the compiled bundle is missing
3. Wire the daemon app to serve:
   - `/assets/*`
   - `/`
   - `/projects`
   - `/projects/...` SPA routes
4. Update the frontend central API client so daemon-served bootstrap context is preferred over manual browser storage while preserving dev/test override compatibility.
5. Add bounded daemon integration tests for HTML shell, asset serving, SPA fallback, and missing-build failure behavior.
6. Update frontend bounded checks and runtime notes to reflect the delivered daemon-served path.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_web_frontend_runtime.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- The daemon serves the compiled frontend shell and built assets from the daemon origin.
- Browser routes under `/projects...` resolve through SPA fallback instead of requiring a separate Vite server.
- The daemon-served HTML injects the frontend auth/bootstrap context so the browser does not require manual token setup for same-origin runtime use.
- The frontend central API client consumes the daemon-served bootstrap context without breaking dev/test override paths.
- Missing compiled assets fail clearly.
- The governing task plan and development log reference each other.
- The documented verification commands are run and recorded honestly.
