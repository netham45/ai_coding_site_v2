# Frontend Website UI Top-Level Creation Contract

## Purpose

Propose the browser-facing daemon contract for creating a new top-level node from the website.

This is a working note, not an implementation plan.

## Recommendation

Use a dedicated project-scoped route for website top-level creation rather than overloading generic manual-node creation further.

Suggested route:

- `POST /api/projects/{project_id}/top-level-nodes`

Why this shape:

- the website creation flow is explicitly project-scoped
- top-level creation now carries source-repo bootstrap semantics
- it keeps parentless website creation distinct from generic child/manual node creation

## Relationship To Existing Backend

Current backend baseline:

- `/api/workflows/start` already creates a top-level node, compiles it, and can start the first run

Current missing piece:

- repo-backed bootstrap from the selected source repo under `repos/`

So this proposed contract should be understood as:

- a website-oriented evolution of the current top-level workflow-start behavior
- not a totally unrelated new flow

## Proposed Request

```json
{
  "kind": "epic",
  "title": "Refactor daemon website operator UI",
  "prompt": "Create the initial workflow for the frontend operator UI.",
  "start_run": true
}
```

## Request Field Rules

### `project_id`

Source:

- route parameter

Meaning:

- selected source repo from the daemon-managed project catalog

Rules:

- required
- must exist in the daemon project catalog

### `kind`

Meaning:

- requested top-level node kind

Rules:

- required
- must be one of the daemon-declared top-level kinds

### `title`

Meaning:

- operator-entered title for the new top-level node

Rules:

- required
- trimmed
- non-empty
- max length should align with the current backend schema unless migrated

Current backend constraint:

- current hierarchy-node and node-version title storage is `String(255)`

### `prompt`

Meaning:

- operator-entered starting prompt for the new top-level node

Rules:

- required
- non-empty
- no deeper content-quality rules in v1

### `start_run`

Meaning:

- whether the daemon should admit and start the first run immediately after successful compile

Rules:

- optional
- defaults to `true`

## Proposed Success Response

```json
{
  "status": "started",
  "project": {
    "project_id": "repo_alpha",
    "label": "repo_alpha"
  },
  "source_repo": {
    "project_id": "repo_alpha",
    "source_path": "repos/repo_alpha",
    "default_branch": "main"
  },
  "bootstrap": {
    "repo_bootstrap_status": "bootstrapped",
    "worker_repo_path": ".aicoding/worktrees/node_100",
    "branch_name": "node-100-v1",
    "seed_commit_sha": "abc123"
  },
  "node": {
    "node_id": "node_100",
    "parent_node_id": null,
    "kind": "epic",
    "tier": "epic",
    "title": "Refactor daemon website operator UI",
    "prompt": "Create the initial workflow for the frontend operator UI.",
    "created_via": "manual"
  },
  "node_version": {
    "id": "nv_100",
    "logical_node_id": "node_100",
    "version_number": 1,
    "title": "Refactor daemon website operator UI",
    "prompt": "Create the initial workflow for the frontend operator UI.",
    "active_branch_name": "node-100-v1",
    "seed_commit_sha": "abc123",
    "final_commit_sha": null
  },
  "compile": {
    "status": "compiled",
    "node_version_id": "nv_100",
    "logical_node_id": "node_100",
    "compile_context": {}
  },
  "lifecycle": {
    "node_id": "node_100",
    "lifecycle_state": "READY",
    "run_status": "RUNNING",
    "current_run_id": "run_100",
    "current_task_id": null,
    "current_subtask_id": null,
    "current_subtask_attempt": null,
    "last_completed_subtask_id": null,
    "execution_cursor_json": {},
    "failure_count_from_children": 0,
    "failure_count_consecutive": 0,
    "defer_to_user_threshold": 0,
    "is_resumable": false,
    "pause_flag_name": null,
    "working_tree_state": null,
    "updated_at": "2026-03-11T12:00:00Z"
  },
  "run_admission": {
    "status": "admitted"
  },
  "run_progress": {
    "node_id": "node_100",
    "node_run_id": "run_100"
  },
  "route_hint": {
    "node_id": "node_100",
    "tab": "overview",
    "url": "/projects/repo_alpha/nodes/node_100/overview"
  }
}
```

## Response Design Notes

### Reuse direction

Most of this response should reuse or closely mirror existing daemon models:

- workflow start response
- hierarchy node response
- node version response
- lifecycle response

### Added website-oriented fields

The website-oriented additions are mainly:

- project context
- source repo bootstrap summary
- route hint

### Why route hint is acceptable

The route hint should be treated as convenience metadata, not core authority state.

The frontend can still derive the route itself, but the response can make the intended landing path explicit.

## Proposed Failure Codes

Suggested machine-readable failure codes include:

- `project_not_found`
- `project_repo_unavailable`
- `invalid_top_level_kind`
- `blank_title`
- `title_too_long`
- `blank_prompt`
- `repo_bootstrap_failed`
- `compile_failed`
- `start_blocked`

## Minimal Alternative

If adding a new route feels too heavy, a smaller alternative is:

- extend `POST /api/workflows/start`
- add `project_id`
- add the repo-bootstrap fields to its response

Current recommendation remains:

- prefer the project-scoped route because it matches the website flow more clearly

## Frontend Expectations

The frontend should treat this request as:

- one create mutation
- one success path that redirects to the new root node
- one inline error path that keeps the form intact

## Related Notes

- `2026-03-11_top_level_node_creation_flow.md`
- `2026-03-11_v1_scope_freeze.md`
- `2026-03-11_phase_2_feature_implementation.md`
