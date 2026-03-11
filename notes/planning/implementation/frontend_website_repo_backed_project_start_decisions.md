# Frontend Website Repo-Backed Project Start Decisions

## Summary

Web feature `05_repo_backed_project_start_and_top_level_bootstrap` now makes project-scoped top-level website creation bootstrap the selected source repo into the created node version's live git repo before success is returned to the browser.

## Decisions

### 1. The website project-start route now owns its own create/bootstrap/compile/start sequence

- `POST /api/projects/{project_id}/top-level-nodes` no longer proxies directly to the generic top-level workflow-start helper
- instead it now performs:
  - project resolution
  - top-level node/version creation
  - source-lineage capture
  - source-repo-backed live git bootstrap
  - workflow compile
  - lifecycle transition to `READY`
  - optional run admission

This keeps the generic CLI startup flow intact while letting the website honor the selected project repo.

### 2. Repo bootstrap reuses the existing live-git substrate

- the daemon now uses `bootstrap_live_git_repo(...)` with a selected `source_repo_path`
- the top-level node version repo is cloned from the chosen source repo under `repos/`
- the cloned repo has its `origin` remote removed
- the daemon checks out the node version's canonical branch name at the selected source repo HEAD commit

This avoids inventing a separate top-level git bootstrap mechanism.

### 3. The project-create response now returns real bootstrap metadata

- the website create response now includes a `bootstrap` object instead of the earlier top-level `repo_bootstrap_status = "deferred"` placeholder
- that object reports:
  - `repo_bootstrap_status`
  - `worker_repo_path`
  - `branch_name`
  - `seed_commit_sha`
  - `head_commit_sha`
  - `working_tree_state`

This makes project selection materially affect the created workflow.

### 4. Source repos must be actual git repositories

- a selected project directory under `repos/` is no longer enough on its own
- the repo-backed create path now requires the selected project directory to contain a valid git repo with a readable `HEAD` commit
- non-git directories are rejected clearly by the daemon

The broader project-selector readiness and labeling work remains in the later corrective feature:

- `plan/web/features/06_project_selector_context_and_bootstrap_readiness.md`

### 5. Real git E2E proof now exists for the website-facing route

- a new real daemon/API E2E test starts from an actual repo under `repos/`
- it calls the website-facing project create route directly
- it verifies the created node version's branch and live git status reflect the selected source repo HEAD

### 6. CLI parity now exists for repo-backed project start

- `workflow start --project <repo>` now routes through the same project-scoped repo-backed create path
- this keeps repo-backed startup from remaining website-only
- plain `workflow start` without `--project` still uses the generic top-level startup route

## Testing

This slice was verified with:

- daemon integration coverage for:
  - valid repo-backed project create
  - non-git project rejection
  - project bootstrap root resolution
  - downstream action catalog compatibility
- real git E2E coverage for the website-facing route
- frontend unit and build proof

## Remaining Gaps

- the project selector screen still needs daemon/context and bootstrap-readiness cues:
  - `plan/web/features/06_project_selector_context_and_bootstrap_readiness.md`
- the tree still needs the remaining required v1 filters:
  - `plan/web/features/07_tree_filter_completion.md`
- the remaining agreed v1 actions still need fuller browser execution closure:
  - `plan/web/verification/03_v1_action_and_shared_state_browser_closure.md`
