# Frontend Website Project Bootstrap And Selection Decisions

## Summary

Web feature `00_project_bootstrap_and_selection` now replaces the placeholder website projects route with a real daemon-backed project catalog and top-level creation flow.

That slice established the route shape and form flow, but the repo-backed project-start behavior itself now lives in the corrective implementation note:

- `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`

The corrective follow-up for project-selector context and bootstrap readiness is now complete in the shipped website surface.

## Decisions

### 1. Website project discovery is rooted at `workspace_root / repos`

- `GET /api/projects` now lists directories under `AICODING_WORKSPACE_ROOT/repos`
- when `AICODING_WORKSPACE_ROOT` is unset, the daemon falls back to `Path.cwd() / "repos"`
- the website treats each directory name as both `project_id` and the default display label

### 2. Website top-level creation is project-scoped

- the browser now uses `POST /api/projects/{project_id}/top-level-nodes`
- that route validates the selected project against the daemon-managed project catalog
- after validation it reuses the existing `start_top_level_workflow(...)` runtime path rather than introducing a second top-level lifecycle implementation

### 3. Repo-backed top-level bootstrap was completed in the corrective follow-up slice

- the project-scoped create route now clones the selected source repo into the created top-level node version repo
- the route now returns a real `bootstrap` object instead of the old deferred placeholder
- the implementation details and proof surface are recorded in:
  - `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`

### 4. The website create flow uses inline confirmation

- the operator selects a project, then enters kind, title, and prompt on the project route
- `Create Node` enters an inline confirmation state
- the confirmation state exposes `create node` and `keep editing`
- successful creation navigates to the returned node overview route

### 5. Runtime API configuration is browser-session driven

- the shared Axios client now reads runtime API configuration from browser storage
- supported keys are:
  - `aicoding.apiBaseUrl`
  - `aicoding.apiToken`
- this allows Playwright to point the built website at a deterministic mock daemon without rebuilding the app for each scenario

### 6. The project catalog now includes daemon context and bootstrap-readiness metadata

- `GET /api/projects` now returns:
  - `daemon_context`
  - readiness metadata for each listed project
- daemon context now includes:
  - reachability state
  - auth status
  - daemon app name
  - daemon version
  - authority
  - session backend
- each project entry now includes:
  - `bootstrap_ready`
  - `readiness_code`
  - `readiness_message`
  - `default_branch`
  - `head_commit_sha`

### 7. The projects screen now renders explicit readiness and failure states

- bootstrap-ready projects remain clickable entry points
- non-ready projects render as disabled project cards with an explicit readiness reason
- the projects route now renders dedicated invalid-auth and daemon-unreachable states instead of only a generic error card

## Testing

This slice was verified with:

- daemon integration coverage for project catalog, empty catalog, invalid project rejection, and successful top-level creation
- bounded frontend checks for the real projects page and top-level creation form scaffold
- Vite production build proof
- Playwright browser proof for project selection, inline confirmation, create-node POST, and redirect
- daemon integration coverage for project readiness classification
- Playwright browser proof for project-selector daemon context, readiness-problem, invalid-auth, and daemon-unreachable states

## Remaining Gaps

- the project selector only covers website-scoped repo discovery; it does not narrow or replace the broader CLI workflow-start behavior
- tree, detail tabs, and the bounded action surface still remain in later website feature phases
