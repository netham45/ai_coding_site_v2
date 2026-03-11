# Web Feature 05: Repo-Backed Project Start And Top-Level Bootstrap

## Goal

Make website project selection materially start work from the selected source repo by bootstrapping the chosen `repos/<project>` git repo into the new top-level node version's worker repo and branch before the browser treats creation as successful.

## Rationale

- Rationale: The current website project selector and top-level creation route establish project context, but they still stop short of cloning the selected source repo into the created top-level node's live working repo.
- Reason for existence: This phase exists to close the most important remaining website v1 gap so choosing a project in the browser actually determines the repo state the new workflow starts from.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

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

- Database: reuse current node-version branch and seed/final commit metadata where possible; only extend durable records if the existing workflow-event and live-git artifacts are insufficient to reconstruct top-level repo bootstrap.
- CLI: do not add a website-only git model; the resulting top-level node must remain inspectable through existing CLI workflow and git/status surfaces even if the initiating route is website-specific.
- Daemon: extend `POST /api/projects/{project_id}/top-level-nodes` so it validates the selected repo under `repos/`, creates the top-level node/version, bootstraps the live git repo from the selected source repo, checks out the canonical top-level branch, records seed metadata, and only then returns success.
- YAML: not applicable; repo bootstrap legality and execution must remain code-owned rather than YAML-driven.
- Prompts: preserve the operator-entered title and prompt as the top-level workflow inputs while ensuring repo bootstrap failure does not silently discard or misattribute them.
- Tests: add daemon integration coverage for successful source-repo bootstrap, invalid repo rejection, non-git repo rejection, bootstrap failure handling, and browser proof that project creation only succeeds when the repo-backed bootstrap succeeds.
- Performance: keep local project bootstrap responsive enough for normal operator use and document any known performance-sensitive clone paths.
- Notes: update the website contract and implementation notes so the shipped behavior and remaining gaps are described honestly before and after this feature lands.

## Planned Work

1. Extend project-catalog validation so website-visible projects are not only directories under `repos/`, but valid bootstrap candidates for top-level git startup.
2. Define the daemon-owned project-start sequence explicitly:
   - resolve `repos/<project_id>`
   - validate it is a usable git repo
   - create the top-level node/version through the existing workflow-start path
   - bootstrap the new node version's live git repo from the selected source repo rather than an empty synthetic seed
   - check out the canonical branch for the new node version
   - record the resulting seed commit and working-tree status
   - compile and optionally start the workflow only after repo bootstrap is in a known-good state
3. Replace the current `repo_bootstrap_status = "deferred"` placeholder with an actual bootstrap object that reports worker repo path, branch name, seed commit, and source-repo metadata.
4. Make failure handling explicit:
   - selected project directory missing
   - selected project is not a git repo
   - git clone/bootstrap failure
   - branch bootstrap failure
   - compile or run-admission failure after repo bootstrap
5. Keep the website flow inline and inspectable:
   - browser create flow should stay on the form when repo bootstrap fails
   - success redirect should only happen after repo-backed bootstrap and top-level create succeed together
6. Update the deterministic browser harness so mock scenarios mirror the corrected daemon contract rather than the current deferred placeholder.
7. Add a real git E2E narrative that starts from an actual repo under `repos/`, creates a top-level node from the website-facing daemon route, and proves that the created node version repo and branch are rooted in the selected source repo.

## Implementation Notes

- The current daemon already has the crucial runtime primitive `bootstrap_live_git_repo(...)`; this phase should reuse that substrate rather than inventing a second top-level git bootstrap implementation.
- The main missing bridge is between the project-scoped website create route and the live-git bootstrap path.
- This phase should treat the currently shipped website project-start flow as `partial`, not `complete`.

