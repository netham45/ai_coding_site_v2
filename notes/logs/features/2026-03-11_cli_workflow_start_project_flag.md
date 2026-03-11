# Development Log: CLI Workflow Start Project Flag

## Entry 1

- Timestamp: 2026-03-11
- Task ID: cli_workflow_start_project_flag
- Task title: CLI workflow start project flag
- Status: started
- Affected systems: cli, daemon, notes, plans, development logs, tests
- Summary: Started the CLI follow-up slice to add a `--project` flag to `workflow start` so the CLI can reach the repo-backed project-start path rather than leaving that flow website-only.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_cli_workflow_start_project_flag.md`
  - `plan/features/37_F10_top_level_workflow_creation_commands.md`
  - `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '540,610p' src/aicoding/cli/parser.py`
  - `sed -n '1210,1245p' src/aicoding/cli/handlers.py`
  - `sed -n '160,210p' tests/unit/test_cli.py`
  - `sed -n '1,110p' tests/integration/test_workflow_start_flow.py`
- Result: Confirmed the current gap. `workflow start` still only calls `/api/workflows/start`, so repo-backed project start is not available through the CLI.
- Next step: Add the `--project` flag, make the project-scoped daemon request accept an optional title, add parser/integration/real-E2E proof, and update the implementation notes.

## Entry 2

- Timestamp: 2026-03-11
- Task ID: cli_workflow_start_project_flag
- Task title: CLI workflow start project flag
- Status: complete
- Affected systems: cli, daemon, notes, plans, development logs, tests
- Summary: Completed the CLI parity slice for repo-backed project start. `workflow start` now accepts `--project`, routes to the project-scoped repo-backed daemon path when present, preserves the existing no-project behavior otherwise, and supports omitted titles through daemon-side title resolution.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_cli_workflow_start_project_flag.md`
  - `plan/features/37_F10_top_level_workflow_creation_commands.md`
  - `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_cli.py tests/integration/test_workflow_start_flow.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_cli_workflow_start_project_real.py -q -m e2e_real`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The CLI can now start a repo-backed top-level workflow from a selected project repo, and the flow is proven through parser coverage, CLI integration coverage, and a real git E2E test.
- Next step: Continue the remaining website v1 corrective phases for project-selector context/readiness, tree filters, and broader browser-proof closure.
