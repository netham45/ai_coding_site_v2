# Task: Web Setup 04 Mock Daemon Harness Bootstrap

## Goal

Implement the fifth website setup phase by creating a deterministic daemon-presented scenario harness for browser testing, with at least one project-catalog scenario and one tree scenario proven through HTTP.

## Rationale

- Rationale: The website now has the planned app, data foundation, and Playwright bootstrap, but browser tests still only prove the placeholder shell and not any daemon-shaped responses.
- Reason for existence: This task exists to establish the first deterministic browser-test harness that looks like daemon HTTP behavior without jumping ahead into full live orchestration setup for every browser test.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/web/setup/04_mock_daemon_harness_bootstrap.md`
- `plan/web/verification/00_browser_harness_and_e2e_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/planning/implementation/fastapi_dependency_and_auth_foundation_decisions.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
- `notes/planning/implementation/frontend_website_playwright_bootstrap_decisions.md`

## Scope

- Database: use deterministic seeded or static scenario state only as needed for the harness; this phase should not introduce new durable product-schema behavior.
- CLI: not applicable; no Python CLI changes in this phase.
- Daemon: add a deterministic scenario-backed HTTP surface or equivalent lightweight harness that preserves daemon-like auth and route behavior for browser tests.
- Website: add the frontend-side wiring needed to consume the deterministic scenario server during browser proof, without expanding into real feature implementation.
- YAML: not applicable; no YAML behavior or schema changes in this phase.
- Prompts: not applicable; no prompt assets or prompt contracts change in this phase.
- Tests: prove at least one project-catalog scenario and one tree scenario through the harness.
- Performance: keep scenarios cheap to boot and deterministic.
- Notes: document the scenario families, harness shape, and current bootstrap limits.

## Planned Changes

1. Add a lightweight deterministic scenario server or equivalent harness owned by the repo.
2. Define at least one project-catalog scenario and one tree scenario.
3. Add proof commands or scripts that exercise the scenario server over HTTP.
4. Update frontend/bootstrap notes to record the harness shape and scenario expectations.
5. Record the work in the setup-family development log.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

Additional harness proof commands should be added in the implementation itself once the exact scenario server entrypoint exists.

## Exit Criteria

- A deterministic daemon scenario harness or equivalent exists for browser tests.
- At least one project scenario exists.
- At least one tree scenario exists.
- The harness can serve those scenarios over HTTP.
- The harness shape and scenario expectations are documented.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
