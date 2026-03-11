# Web Feature 08: Daemon-Served Compiled Frontend And Auth Bootstrap

## Goal

Make the daemon serve the compiled website bundle on port `8000` and provide the browser with the daemon auth/bootstrap context automatically when the website is loaded from that daemon.

## Rationale

- Rationale: The current website requires a separate Vite server on `5173` plus manual browser `localStorage` setup for API base URL and bearer token, which is not an acceptable operator-facing runtime posture for the normal daemon workflow.
- Reason for existence: This phase exists to turn the website into a real daemon-owned operator surface that can be opened directly from the daemon origin without a separate frontend boot step or manual token copy/paste.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
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

- Database: no schema change is expected by default; the feature should reuse the existing daemon auth token and existing project/node read models.
- CLI: no new CLI flow is required for normal website access, but CLI inspection and auth-token reporting should stay aligned with the daemon-served website posture.
- Daemon: add compiled-asset serving, SPA route fallback for browser routes, a daemon-served frontend bootstrap payload, and a clear startup posture when compiled assets are missing.
- Website: consume daemon-served bootstrap context instead of requiring manual `localStorage` token injection for the daemon-served runtime; keep separate Vite development ergonomics intact.
- YAML: not applicable.
- Prompts: not applicable directly, but the daemon-served website must preserve prompt, action, and project flows already planned for the browser.
- Tests: add daemon integration coverage for static bundle serving and frontend bootstrap context, plus real browser proof against the daemon origin on port `8000`.
- Performance: static bundle delivery and bootstrap payload generation should remain lightweight at daemon startup and first-page load.
- Notes: update operator-facing website access notes and frontend communication notes so the normal runtime and dev-runtime split are explicit.

## Planned Work

1. Define the daemon-owned runtime split explicitly:
   - development mode continues to use Vite on `5173`
   - operator/runtime mode serves the compiled frontend from the daemon origin on `8000`
2. Add a daemon-served compiled-asset path:
   - load `frontend/dist` or packaged equivalent
   - serve static assets without interfering with `/api/*`
   - return the SPA entry document for browser routes such as `/projects` and `/projects/:projectId/...`
3. Add a daemon-served frontend bootstrap surface:
   - API base URL for same-origin use
   - bearer-token bootstrap for the current daemon instance
   - any minimal daemon identity or environment fields the frontend already expects centrally
4. Change the frontend auth/bootstrap strategy for daemon-served runtime:
   - prefer daemon-served bootstrap context first
   - keep `localStorage` and env overrides available for Vite dev, mock-daemon, and Playwright scenarios
   - avoid making each feature module read auth independently
5. Decide and document the bootstrap transport:
   - inline script in the served HTML, or
   - dedicated bootstrap JSON or JS endpoint loaded before app startup
   - the chosen path must be same-origin, deterministic, and easy to integration-test
6. Harden startup and packaging behavior:
   - if compiled assets are missing, daemon startup or website routes should fail clearly rather than silently serving broken HTML
   - document the canonical build step needed before claiming the daemon-served website is available
7. Add proving at the right layers:
   - daemon integration tests for static file serving, SPA fallback, and auth/bootstrap payload shape
   - bounded frontend proof that bootstrap context is consumed correctly
   - real browser E2E against the real daemon origin on `8000` without manual token injection

## Implementation Notes

- The current frontend client already centralizes auth lookup in `frontend/src/lib/api/client.js`; this phase should extend that central path rather than introducing feature-local token handling.
- The daemon-served website should default to same-origin `/api` and should not require users to set `aicoding.apiBaseUrl` or `aicoding.apiToken` manually for normal runtime use.
- This phase should not remove the separate Vite dev server workflow; it should add a normal runtime path, not replace frontend development ergonomics.
- Packaging and install posture matters here: if the daemon is expected to serve compiled assets outside a repo checkout, the plan must account for how built frontend assets are bundled or located.
