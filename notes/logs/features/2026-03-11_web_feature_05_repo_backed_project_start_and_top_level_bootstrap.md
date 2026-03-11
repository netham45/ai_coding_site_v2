# Development Log: Web Feature 05 Repo-Backed Project Start And Top-Level Bootstrap

## Entry 1

- Timestamp: 2026-03-11
- Task ID: web_feature_05_repo_backed_project_start_and_top_level_bootstrap
- Task title: Web feature 05 repo-backed project start and top-level bootstrap
- Status: started
- Affected systems: daemon, website, notes, plans, development logs, tests
- Summary: Started the corrective website feature slice that makes project-scoped top-level creation bootstrap the selected source repo into the created top-level node version repo before the browser treats creation as successful.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_web_feature_05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
  - `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `sed -n '1,260p' src/aicoding/daemon/projects.py`
  - `sed -n '1,320p' src/aicoding/daemon/live_git.py`
  - `sed -n '1,340p' src/aicoding/daemon/workflow_start.py`
- Result: Confirmed the current route still returns `repo_bootstrap_status = "deferred"` and never enters the live-git bootstrap path. The corrective implementation needs a project-specific create/bootstrap/compile/start sequence.
- Next step: Extend live-git bootstrap for selected source repos, refactor the project create route to use it, add integration and real E2E proof, and update the contract/implementation notes.

## Entry 2

- Timestamp: 2026-03-11
- Task ID: web_feature_05_repo_backed_project_start_and_top_level_bootstrap
- Task title: Web feature 05 repo-backed project start and top-level bootstrap
- Status: complete
- Affected systems: daemon, website, notes, plans, development logs, tests
- Summary: Completed the corrective repo-backed project-start slice. The project-scoped create route now bootstraps the created top-level node version repo from the selected source repo, returns real bootstrap metadata, rejects non-git source directories, and is proven through integration plus real git E2E coverage.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_web_feature_05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
  - `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/integration/test_web_project_bootstrap_api.py tests/integration/test_web_explorer_tree_api.py tests/integration/test_web_actions_api.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_bootstrap_real.py -q -m e2e_real`
  - `cd frontend && npm run test:unit`
  - `cd frontend && npm run build`
  - `python3 -m pytest tests/unit/test_task_plan_docs.py -q`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The route now returns a real `bootstrap` object, the created top-level node version is rooted in the selected source repo HEAD commit, and the remaining website v1 gaps have narrowed to project-selector context/readiness, tree filters, and broader browser-proof closure.
- Next step: Continue with `plan/web/features/06_project_selector_context_and_bootstrap_readiness.md`.
