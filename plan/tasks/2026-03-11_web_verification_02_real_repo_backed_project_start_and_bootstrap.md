# Task: Web Verification 02 Real Repo-Backed Project Start And Bootstrap

## Goal

Add the missing real browser E2E proof for repo-backed website project start so the website no longer relies only on daemon/API real-E2E evidence for that flow.

## Rationale

- Rationale: The project-scoped repo-backed create route is already real-E2E proven at the daemon/API layer, but the remaining website-specific gap is a browser-driven run against the real daemon-served frontend.
- Reason for existence: This task exists to close the final proof gap for the repo-backed website start flow by driving the actual browser UI against the real daemon and then inspecting the resulting durable git/version state.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/web/verification/02_real_repo_backed_project_start_and_bootstrap.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`
- `notes/planning/implementation/frontend_website_browser_harness_matrix_adoption.md`

## Scope

- Database: inspect the created authoritative node/version through real daemon or CLI surfaces after the browser flow completes.
- CLI: use existing CLI audit/git inspection commands to validate the resulting repo-backed state rather than trusting only browser redirect.
- Daemon: run the actual daemon process, with real auth bootstrap and frontend asset serving, against a real git repo under `repos/`.
- Website: drive the actual project-selection and top-level creation flow through Playwright against the daemon-served frontend.
- YAML: not applicable.
- Prompts: prove that the browser-entered title and prompt survive the repo-backed create flow.
- Tests: add one `e2e_real` pytest wrapper around a real Playwright browser flow plus the current daemon/API real E2E.
- Performance: record any obvious latency from build, bootstrap, and redirect during the real browser run.
- Notes: update the E2E command catalog and website verification audit so the new real browser checkpoint is tracked explicitly.

## Planned Changes

1. Add the governing task plan and development log for verification phase 02.
2. Add a Playwright config for real-daemon runs that does not start the mock `vite preview` web server.
3. Add a real browser spec that:
   - opens the daemon-served frontend
   - selects the repo-backed project
   - submits top-level creation through the website form
   - waits for the overview redirect
   - writes the created node id to a result file for pytest-side inspection
4. Add a pytest `e2e_real` test that:
   - builds the frontend bundle
   - launches the real daemon harness
   - seeds a real source repo under `repos/`
   - runs the Playwright browser spec
   - inspects the created node/version through real CLI/API surfaces
5. Update the website audit, browser harness note, and E2E command docs to record the new checkpoint honestly.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run build
PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_bootstrap_real.py tests/e2e/test_web_project_top_level_browser_real.py -q -m e2e_real
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a real browser E2E runs against the real daemon-served frontend, not the mock-daemon harness
- the browser flow creates a top-level node from a real git repo under `repos/`
- the created node/version is inspected through real CLI/API surfaces and proves repo-backed bootstrap metadata
- the verification audit no longer lists real repo-backed browser proof as missing
- the E2E command docs include the new real browser checkpoint
- the governing task plan and development log reference each other
- the documented verification commands are run and their results are recorded honestly
