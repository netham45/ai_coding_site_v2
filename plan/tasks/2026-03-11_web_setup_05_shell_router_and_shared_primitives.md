# Task: Web Setup 05 Shell Router And Shared Primitives

## Goal

Implement the sixth website setup phase by adding the route skeleton, persistent app shell structure, and the shared loading/empty/error/status primitives that later feature phases will reuse.

## Rationale

- Rationale: The frontend now has the runtime, data-access foundation, Playwright bootstrap, and deterministic scenario harness, but it still lacks the route skeleton and shared UI primitives the feature plans assume.
- Reason for existence: This task exists to freeze the shell and primitive layer before real feature routes land, so later pages do not invent inconsistent layout, navigation, and loading/error patterns.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/web/setup/05_shell_router_and_shared_primitives.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
- `notes/planning/implementation/frontend_website_mock_daemon_harness_decisions.md`

## Scope

- Database: not applicable; this phase does not change durable product-state schema.
- CLI: not applicable; no Python CLI changes in this phase.
- Daemon: keep route meaning and shell shape aligned with daemon-backed URLs and future browser surfaces.
- Website: add the route skeleton, persistent shell regions, shared UI primitives, and stable bootstrap test ids.
- YAML: not applicable; no YAML behavior or schema changes in this phase.
- Prompts: not applicable; no prompt assets or prompt contracts change in this phase.
- Tests: prove the routes and shared primitives render through bounded checks.
- Performance: keep the shell lightweight and avoid feature-heavy data loading in this phase.
- Notes: document the shared primitive expectations, route skeleton, and stable test-id conventions now adopted in code.

## Planned Changes

1. Add the router dependency and base route configuration.
2. Add the persistent shell layout and placeholder route pages.
3. Add shared loading, empty, error, and status primitives.
4. Add stable `data-testid` markers for the shell and route placeholders.
5. Extend the bounded frontend proof to verify the route skeleton and shared primitives.
6. Document the resulting route and primitive conventions.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- Route skeleton exists.
- Shared loading/empty/error/status primitives exist.
- Stable test-id conventions exist in the scaffold.
- The bounded frontend proof covers the route skeleton and shared primitives.
- The route and primitive conventions are documented.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
