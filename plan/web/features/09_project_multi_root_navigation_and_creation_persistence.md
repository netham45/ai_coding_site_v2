# Web Feature 09: Project Multi-Root Navigation And Creation Persistence

## Goal

Preserve project-scoped top-level creation even after a project already has one or more top-level nodes, and make the website navigate multi-root projects explicitly instead of collapsing them into a single latest-root redirect.

## Rationale

- Rationale: The current project route assumes one effective root per project and hard-redirects to the latest created root, which traps operators out of the creation UI and hides earlier top-level nodes.
- Reason for existence: This feature exists to bring the website back in line with the project-scoped creation flow and real multi-root behavior the underlying system already permits.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/02_F01_configurable_node_hierarchy.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `AGENTS.md`

## Scope

- Database: rely on existing durable project-start workflow events and root-node records; only extend persistence if current bootstrap lookup cannot describe multiple top-level nodes safely.
- CLI: keep website project views aligned with existing top-level workflow creation semantics rather than inventing a website-only root concept.
- Daemon: replace the singular `root_node_id` project bootstrap assumption with a project-scoped root catalog or equivalent route that can surface multiple top-level nodes plus a recommended landing target.
- Website: keep `/projects/:projectId` as a usable project workspace that can still show the creation surface, existing top-level nodes, and explicit navigation into any selected root.
- YAML: not applicable.
- Prompts: preserve existing top-level prompt/title entry semantics while making repeated top-level creation inspectable rather than hidden.
- Tests: cover multi-root project bootstrap payloads, project-route rendering when roots already exist, create-another-root behavior, and explicit navigation among existing roots.
- Performance: project bootstrap and root listing should remain lightweight even when a project has many top-level nodes.
- Notes: update website routing and creation-flow notes so they describe the multi-root project surface honestly.

## Planned Work

1. Replace the current project-bootstrap read model with a shape that can describe:
   - zero roots
   - one root
   - many roots
   - a daemon-recommended landing node when helpful
2. Keep `/projects/:projectId` renderable even when roots exist:
   - show the top-level creation form
   - show existing top-level nodes for the selected project
   - make entering a root node an explicit operator choice rather than an unconditional redirect
3. Decide and document whether the project page should default to:
   - creation plus root catalog
   - creation plus most-recent root preview
   - redirect only when a route hint is explicitly requested
4. Add browser affordances for returning from a node detail route to the project workspace without losing project context.
5. Update mock-daemon scenarios and browser tests so they exercise projects with multiple existing top-level nodes instead of only zero-root and one-root cases.

## Notes

- The underlying daemon already allows repeated top-level creation; the website currently narrows that behavior silently through project bootstrap and routing assumptions.
- This phase should correct the narrowing rather than treating single-root projects as a v1 requirement.
