# Development Log: Web Repo-Backed Project Start Planning

## Entry 1

- Timestamp: 2026-03-11
- Task ID: web_repo_backed_project_start_planning
- Task title: Web repo-backed project start planning
- Status: started
- Affected systems: notes, plans, development logs
- Summary: Started a corrective planning pass after reviewing the current website project-selection implementation and confirming that the selected project still does not bootstrap the chosen source repo into the created top-level node's worker repo.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_web_repo_backed_project_start_planning.md`
  - `plan/web/features/00_project_bootstrap_and_selection.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
  - `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,240p' plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `sed -n '1,260p' notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
  - `sed -n '1,260p' notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `sed -n '1,260p' src/aicoding/daemon/projects.py`
  - `sed -n '1,320p' src/aicoding/daemon/live_git.py`
- Result: Confirmed the exact mismatch. The website create route exists, but it still returns `repo_bootstrap_status = "deferred"` and never calls the live-git bootstrap path. A corrective authoritative web feature plan is required.
- Next step: Add the missing web feature and verification plans, update the current implementation and future-plan notes to mark the shipped state as partial, and rerun the document-schema tests.

## Entry 2

- Timestamp: 2026-03-11
- Task ID: web_repo_backed_project_start_planning
- Task title: Web repo-backed project start planning
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added a corrective authoritative web feature plan for repo-backed project start and top-level bootstrap, added a paired verification plan for real repo-backed proof, and updated the current website project-bootstrap notes so the shipped state is described honestly as partial until the corrective feature lands.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_web_repo_backed_project_start_planning.md`
  - `plan/web/features/00_project_bootstrap_and_selection.md`
  - `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
  - `plan/web/verification/02_real_repo_backed_project_start_and_bootstrap.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
  - `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_task_plan_docs.py -q`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The repo no longer relies only on a vague deferred note for this gap; the missing repo-backed project-start work is now an explicit corrective web feature and verification phase, and the current website project-start slice is documented as partial until that work lands.
- Next step: Open the implementation task for `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md` and do not describe website project-start as materially complete until the real repo bootstrap and proof are in place.
