# Task: Web Feature 06 Project Selector Context And Bootstrap Readiness

## Goal

Implement the corrective website feature that makes the projects screen expose daemon/context status and per-project bootstrap readiness instead of only listing directory names under `repos/`.

## Rationale

- Rationale: The current projects screen can start a repo-backed workflow, but it still fails the promised v1 operator role because it hides daemon identity/auth context and does not distinguish valid git start targets from arbitrary directories.
- Reason for existence: This task exists to make the website project selector a real operator entry surface with explicit readiness and failure cues.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/06_project_selector_context_and_bootstrap_readiness.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`

## Scope

- Database: no direct schema work is expected.
- CLI: keep project/start semantics aligned with the `workflow start --project ...` flow and existing operator vocabulary.
- Daemon: expand the website project-catalog read model to include daemon summary and per-project bootstrap readiness metadata.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: cover populated, empty, readiness-problem, invalid-auth, and unreachable project-screen states in daemon/API and browser proof where applicable.
- Performance: the project catalog must remain a lightweight startup read.
- Notes: update the project bootstrap/selection implementation note and any affected future-plan contract notes so they reflect the shipped readiness contract honestly.

## Planned Changes

1. Add this governing task plan and the paired development log for feature 06.
2. Extend the daemon `GET /api/projects` response so it includes:
   - daemon/context summary for the project-selector screen
   - per-project bootstrap-readiness metadata
3. Inspect each project directory under `repos/` and classify bootstrap readiness without mutating anything:
   - valid git repo with readable `HEAD`
   - invalid or unreadable source repo with an explicit reason
4. Update the website projects screen so it renders:
   - daemon/context summary
   - readiness-aware project cards
   - explicit auth-invalid and daemon-unreachable failure states
5. Update the shared frontend API error normalization so daemon auth/unreachable states can be rendered intentionally instead of as generic failures.
6. Add daemon integration coverage plus bounded frontend and Playwright proof for:
   - populated ready catalog
   - empty catalog
   - readiness problem catalog
   - invalid auth
   - unreachable daemon
7. Update the relevant implementation notes and future-plan notes to match the delivered contract.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_web_project_bootstrap_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `GET /api/projects` returns daemon/context summary plus readiness metadata for each listed project.
- The website projects screen shows daemon summary and readiness cues instead of only raw folder links.
- Projects that are not bootstrap-ready are clearly labeled and not presented as equivalent good start targets.
- The browser explicitly distinguishes invalid auth from daemon-unreachable failures on the projects screen.
- The implementation note and future-plan scope note are updated honestly.
- The governing task plan and development log reference each other.
