# Task: Web Setup 03 Playwright Bootstrap

## Goal

Implement the fourth website setup phase by installing Playwright, adding the base browser-test config and artifact paths, and proving one smoke browser test against the existing placeholder shell.

## Rationale

- Rationale: The frontend workspace now has the planned runtime, shell, and transport/query foundations, but it still has no real browser-test layer.
- Reason for existence: This task exists to establish the Playwright foundation early, before feature work begins, so browser verification becomes part of the normal website proving surface rather than a late add-on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`
- `plan/web/setup/03_playwright_bootstrap.md`
- `plan/web/setup/04_mock_daemon_harness_bootstrap.md`
- `plan/web/verification/00_browser_harness_and_e2e_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
- `notes/planning/implementation/frontend_website_axios_query_foundation_decisions.md`

## Scope

- Database: not applicable; this phase does not change durable product-state schema.
- CLI: not applicable; no Python CLI contract changes in this phase.
- Daemon: keep the browser-test foundation compatible with later daemon-backed scenarios, but do not yet implement the mock-daemon harness itself.
- Website: add Playwright dependencies, base config, artifact directories, and one smoke browser test against the existing website shell.
- YAML: not applicable; no YAML behavior or schema changes in this phase.
- Prompts: not applicable; no prompt assets or prompt contracts change in this phase.
- Tests: prove one browser smoke test passes and that artifact output is configured.
- Performance: keep the smoke test practical and lightweight so it remains usable as a repeated bootstrap proof.
- Notes: document the Playwright config, artifact path conventions, and the intended relationship between this smoke proof and the later daemon-backed harness phase.

## Planned Changes

1. Add Playwright dependencies and frontend scripts.
2. Add the base Playwright config with artifact output paths.
3. Add one smoke browser test for the placeholder shell.
4. Add any needed ignore rules for Playwright/browser artifacts.
5. Document the Playwright bootstrap decisions and artifact paths.
6. Record the work in the setup-family development log.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm install
cd frontend && npx playwright install chromium
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- Playwright is installed in the frontend workspace.
- Base Playwright config exists.
- Browser artifacts are configured to a stable path.
- One smoke browser test exists and passes.
- The artifact-path and Playwright bootstrap decisions are documented.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
