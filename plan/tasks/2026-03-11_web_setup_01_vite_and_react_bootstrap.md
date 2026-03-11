# Task: Web Setup 01 Vite And React Bootstrap

## Goal

Implement the second website setup phase by turning the baseline `frontend/` workspace into a functioning Vite and React app with a placeholder shell, canonical app scripts, and bounded proof that the shell renders.

## Rationale

- Rationale: The website workspace baseline now exists, but phase 00 intentionally stopped before any app framework or shell existed.
- Reason for existence: This task exists to create the first real browser-app surface the rest of the website setup can build on, while preserving compatibility with the daemon-owned hosting model and proving the shell actually renders rather than only claiming that the files exist.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/web/setup/01_vite_and_react_bootstrap.md`
- `plan/web/setup/03_playwright_bootstrap.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/planning/implementation/frontend_website_setup_baseline_decisions.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`

## Scope

- Database: not applicable; this phase does not touch durable product-state schema.
- CLI: not applicable; this phase does not change the Python CLI contract.
- Daemon: preserve compatibility with daemon-served or daemon-proxied hosting by keeping the bootstrap app as a normal Vite client rather than introducing a competing runtime model.
- Website: add the Vite config, React entrypoint, placeholder app shell, styles, and canonical frontend scripts needed for the first functioning browser surface.
- YAML: not applicable; no YAML behavior or schema changes in this phase.
- Prompts: not applicable; no prompt assets or prompt contracts change in this phase.
- Tests: add bounded proof that the React app shell renders and verify the frontend builds successfully.
- Performance: keep the bootstrap lightweight and avoid introducing unnecessary framework complexity before later routing/data phases.
- Notes: document the initial frontend entrypoint, placeholder shell contract, and verification commands for the Vite/React bootstrap.

## Planned Changes

1. Update the frontend package manifest with Vite/React scripts and dependencies.
2. Add the initial Vite config and HTML entrypoint.
3. Add the React entrypoint, placeholder app shell, and basic styling.
4. Add bounded frontend render proof for the placeholder shell.
5. Document the initial entrypoint and shell decisions.
6. Record the work in the setup-family development log.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- Vite app files exist under `frontend/`.
- React app files exist under `frontend/`.
- The placeholder shell renders in bounded proof.
- The frontend build succeeds.
- The canonical frontend scripts for `dev`, `build`, and bounded test proof are documented.
- A note records the initial app entrypoint and placeholder-shell decisions.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
