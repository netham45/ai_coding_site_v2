# Task: Web Feature 05 Repo-Backed Project Start And Top-Level Bootstrap

## Goal

Implement the corrective website feature that makes project-scoped top-level creation bootstrap the selected source repo into the created top-level node version's live git repo before success is returned to the browser.

## Rationale

- Rationale: The current website project selector and top-level creation flow establish project context, but they still leave the selected repo disconnected from the created top-level node.
- Reason for existence: This task exists to close the most important remaining website v1 gap so choosing a project in the browser actually determines the repo state the new workflow starts from.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/12_F17_deterministic_branch_model.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`

## Scope

- Database: reuse current node-version branch and seed/final commit metadata plus workflow-event audit where possible; do not add schema without proving the current durable artifacts are insufficient.
- CLI: keep website-triggered top-level creation inspectable through existing CLI workflow, branch, and git status surfaces.
- Daemon: extend the project-scoped top-level create route so it validates the selected source repo, bootstraps the created node version repo from it, records seed metadata, and only then compiles and optionally starts the workflow.
- YAML: not applicable.
- Prompts: preserve the operator-entered title and prompt as top-level workflow inputs throughout the repo-backed create path.
- Tests: add daemon integration coverage, bounded frontend contract updates where needed, and a real git E2E narrative for the website-facing route.
- Performance: keep local clone/bootstrap practical for normal operator startup.
- Notes: update the website creation contract and implementation decision note so the new repo-backed behavior and proof scope are described honestly.

## Planned Changes

1. Add this governing task plan and the paired development log for feature 05.
2. Extend the live-git bootstrap layer to support bootstrapping a node-version repo from an arbitrary selected source repo path under `repos/`.
3. Refactor the project-scoped top-level create path so it performs:
   - project resolution and git-repo validation
   - top-level node/version creation
   - source-lineage capture
   - repo-backed live-git bootstrap for the created node version
   - workflow compile
   - lifecycle transition to `READY`
   - optional run admission/start
4. Replace the current `repo_bootstrap_status = "deferred"` placeholder with a real bootstrap object in the project-scoped create response.
5. Expand daemon integration coverage for valid repo bootstrap, invalid repo rejection, and returned bootstrap metadata.
6. Add a real daemon/API E2E test that starts from an actual repo under `repos/` and proves the created node version repo and branch are rooted in that source repo.
7. Update the website contract and implementation notes to reflect the shipped behavior honestly.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/integration/test_web_project_bootstrap_api.py -q
python3 -m pytest tests/e2e/test_web_project_top_level_bootstrap_real.py -q -m e2e_real
cd frontend && npm run test:unit
cd frontend && npm run build
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `POST /api/projects/{project_id}/top-level-nodes` bootstraps the created top-level node version from the selected source repo instead of returning a deferred placeholder.
- The returned project-create payload includes real bootstrap metadata rather than only `repo_bootstrap_status = "deferred"`.
- Invalid or non-git project directories are rejected clearly.
- The created node version is inspectable through existing git/branch surfaces and shows a seed commit derived from the selected source repo.
- A real git E2E test exists for the website-facing project-start route.
- The implementation note and future-plan contract note are updated honestly.
- The governing task plan and development log reference each other.
