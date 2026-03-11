# Web Feature 06: Project Selector Context And Bootstrap Readiness

## Goal

Complete the project-selector screen so it exposes the daemon/context information promised by the v1 scope and only presents project entries that are meaningful repo-bootstrap candidates for website startup.

## Rationale

- Rationale: The current projects screen mostly lists directories under `repos/` and launches the create form, but it does not yet expose the daemon/auth/context cues required by the v1 scope and it does not distinguish bootstrap-ready git repos from arbitrary directories.
- Reason for existence: This phase exists to make the project selector a real operator entry surface rather than just a list of folder names.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`

## Scope

- Database: no direct schema work is expected by default.
- CLI: keep project/bootstrap semantics aligned with existing operator inspection surfaces where applicable.
- Daemon: expand the website bootstrap/project-catalog read model so it exposes daemon reachability, auth validity, current project context when available, and bootstrap-readiness metadata for each listed project.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover daemon-context rendering, bootstrap-readiness filtering or labeling, invalid-auth or unreachable-daemon presentation where applicable, and project-selector browser behavior.
- Performance: project-catalog and daemon-context reads should remain lightweight at startup.
- Notes: keep the project-selector and top-level create notes aligned with the actual delivered context and readiness contract.

## Planned Work

1. Define the daemon-facing project-selector bootstrap payload explicitly enough for the website to render:
   - available projects
   - daemon reachability summary
   - auth-valid or auth-invalid state
   - daemon build/version or equivalent identity when available
   - bootstrap-readiness fields for each project entry
2. Tighten website-visible project entries so the browser does not imply that any random directory under `repos/` is a valid start target without clear readiness information.
3. Render that context on the projects page rather than limiting the screen to list-plus-form behavior.
4. Keep failure and empty states inline and inspectable instead of collapsing into silent missing-data behavior.
5. Add daemon/API tests, bounded frontend coverage, and Playwright proof for populated, empty, and readiness-problem project-selector states.
