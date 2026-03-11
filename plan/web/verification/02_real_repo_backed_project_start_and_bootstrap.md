# Web Verification 02: Real Repo-Backed Project Start And Bootstrap

## Goal

Prove that website project selection and top-level creation start a workflow from the selected real repo under `repos/` rather than from a repo-disconnected logical placeholder.

## Rationale

- Rationale: The browser currently has deterministic mock-daemon proof for project selection and top-level creation, but the missing high-risk boundary is real repo-backed bootstrap from the selected source repo.
- Reason for existence: This verification phase exists to close that runtime gap with real git-backed proof instead of relying only on mocked or bounded browser scenarios.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: prove that the created top-level node version records the expected branch and seed metadata durably enough for later inspection.
- CLI: where applicable, use existing CLI or daemon-inspection surfaces to confirm the resulting node/version git state rather than trusting only the browser redirect.
- Daemon: run the real project-scoped top-level create route against an actual repo under `repos/` and verify bootstrap success and failure paths through the real API.
- YAML: not applicable for this verification phase.
- Prompts: prove that the operator-entered title and prompt survive the repo-backed create path and are bound to the created node/version correctly.
- Tests: include daemon integration tests, bounded browser regression coverage, and at least one real git E2E narrative that starts from an actual source repo and ends with a created top-level node whose worker repo is rooted in that source repo.
- Performance: record any obvious clone/bootstrap latency issues discovered during real proof.
- Notes: update verification and implementation notes with the exact commands and resulting proof scope.

## Verify

- `GET /api/projects` only lists usable project candidates under `repos/`.
- `POST /api/projects/{project_id}/top-level-nodes` fails clearly when the selected project is missing or not a git repo.
- Successful project-scoped create records non-deferred bootstrap metadata.
- Successful project-scoped create produces a worker repo whose git history is rooted in the selected source repo.
- The created node version exposes the expected canonical branch name and recorded seed commit.
- Browser success redirect happens only after repo-backed bootstrap succeeds.

## Tests

- Daemon integration tests for:
  - valid repo-backed project start
  - missing project
  - non-git project directory
  - bootstrap failure propagation
  - returned bootstrap metadata shape
- Browser bounded and Playwright tests for:
  - success path with corrected bootstrap payload
  - inline create failure when bootstrap fails
  - no redirect on bootstrap failure
- Real E2E target:
  - start from an actual repo under `repos/`
  - call the website-facing project create route through the real daemon
  - inspect the created node/version repo and metadata through real surfaces

## Notes

- This verification phase should be treated as the required real-E2E layer for the website project-start feature.
- Mock-daemon browser proof remains useful for iteration, but it is not the final completion claim for repo-backed project start.
