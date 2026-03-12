# Frontend Website Final Verification Audit

## Purpose

Record the explicit current browser-proof map for the implemented website scope and name the residual gaps honestly.

## Current Verification Surface

### Canonical commands rerun for this audit

- `python3 -m pytest tests/integration/test_web_project_bootstrap_api.py -q`
- `python3 -m pytest tests/integration/test_web_explorer_tree_api.py -q`
- `python3 -m pytest tests/integration/test_web_actions_api.py -q`
- `cd frontend && npm run test:unit`
- `cd frontend && npm run build`
- `cd frontend && npm run test:e2e`
- `python3 -m pytest tests/unit/test_task_plan_docs.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py -q`

## Route Coverage

### Covered routes

- `/`
  - bounded proof: yes
  - Playwright proof: yes
  - notes:
    - lands on the projects index through the routed shell

- `/projects`
  - bounded proof: yes
  - Playwright proof: yes
  - notes:
    - covered as the projects index surface

- `/projects/:projectId`
  - bounded proof: indirect
  - Playwright proof: yes
  - notes:
    - covered through project selection, top-level creation, and root auto-open redirect

- `/projects/:projectId/nodes/:nodeId/:tab`
  - bounded proof: yes
  - Playwright proof: yes for the agreed v1 route and action matrix
  - notes:
    - overview, workflow, runs, prompts, actions, summaries, sessions, and provenance are browser-proven
    - representative loading, empty, blocked, and error permutations are now browser-proven across tree, actions, and prompts surfaces

- `/projects/:projectId/nodes/:nodeId`
  - bounded proof: indirect
  - Playwright proof: indirect
  - notes:
    - covered through redirect behavior into `/overview`

- `/debug/primitives`
  - bounded proof: yes
  - Playwright proof: no
  - notes:
    - treated as a developer support route, not a primary operator route

## Tab Coverage

### Overview

- bounded rendering proof: yes
- Playwright proof: yes
- loading/empty/error proof: bounded partial

### Workflow

- bounded rendering proof: yes
- Playwright proof: yes
- loading/empty/error proof: bounded partial

### Runs

- bounded rendering proof: yes
- Playwright proof: yes
- loading/empty/error proof: bounded partial

### Prompts

- bounded rendering/mutation proof: yes
- Playwright proof: yes
- blocked-live-candidate browser proof: yes

### Actions

- bounded rendering/mutation proof: yes
- Playwright proof: yes
- blocked action browser proof: yes

### Summaries

- bounded rendering proof: yes
- Playwright proof: yes

### Sessions

- bounded rendering proof: yes
- Playwright proof: yes

### Provenance

- bounded rendering proof: yes
- Playwright proof: yes

## Action Coverage

### Browser-proven action flows

- `start_run`
  - daemon/API proof: yes
  - browser proof: yes

- `pause_run`
  - daemon/API proof: yes
  - browser proof: yes

- `resume_run`
  - daemon/API proof: yes
  - browser proof: yes

- `session_attach`
  - daemon/API proof: yes
  - browser proof: yes

- `session_resume`
  - daemon/API proof: yes
  - browser proof: yes

- `session_provider_resume`
  - daemon/API proof: yes
  - browser proof: yes

- `reconcile_children:*`
  - daemon/API proof: yes
  - browser proof: yes

- `regenerate_node`
  - daemon/API proof: yes
  - browser proof: yes

- prompt `save and regenerate`
  - daemon/API proof: yes
  - browser proof: yes
  - note:
    - this lives on the prompts tab rather than the generic actions tab

### Remaining action gap

No remaining agreed v1 browser-owned action is only daemon/API-proven.

## Shared Primitive Coverage

### Covered

- `LoadingState`
  - bounded proof: yes
  - browser proof: yes

- `EmptyState`
  - bounded proof: yes
  - browser proof: yes

- `ErrorState`
  - bounded proof: yes
  - browser proof: yes

- `StatusBadge`
  - bounded proof: yes

### Remaining gap

The remaining shared-state gap is not basic primitive rendering. It is broader screenshot-review automation and deeper permutation closure beyond the agreed v1 action matrix.

## Mutation Invalidation Coverage

### Proven

- top-level creation invalidates project bootstrap enough to reopen the new root flow
- prompt save-and-regenerate invalidates node/project query families enough to refresh the edited prompt state
- action execution invalidates node/project query families enough to refresh action-surface state

### Remaining gap

This is proven by behavior in the current mock/browser flows, but there is not yet a dedicated assertion suite that verifies every intended query family invalidation by name.

## Screenshot And Visual Review Targets

The following screens should be captured and visually reviewed during later hardening or AI-assisted visual review:

- projects index with populated catalog
- project detail creation form before confirmation
- tree sidebar plus overview tab for a root node
- prompts tab in pre-confirmation state
- prompts tab confirmation strip
- actions tab with both legal and blocked actions visible
- provenance tab with raw-json toggle closed

Current status:

- screenshot targets are defined
- screenshot artifacts are now captured in Playwright outputs for selected empty-catalog and blocked-prompt review states
- no explicit AI-assisted screenshot review pass has been implemented yet

## Explicit Untested Or Partially Tested Flows

- browser screenshot review automation beyond simple artifact capture
- explicit query-family invalidation assertions by query key rather than by observed behavior alone

Corrective verification phases:

- `plan/web/verification/02_real_repo_backed_project_start_and_bootstrap.md`

## Audit Result

The current website surface is implemented and browser-proven for the main happy-path narrative:

- project selection
- top-level creation
- tree navigation
- prompt edit and regenerate
- the agreed v1 action matrix
- provenance inspection

The verification surface is still not full-closure for every conceivable route permutation, real repo-backed browser proof, or visual review target.
The verification surface is still not full-closure for every conceivable route permutation or visual review target.

That is acceptable only if the website is described honestly as:

- implemented
- browser-proven for the main happy path
- still carrying named residual browser-proof gaps

It should not be described as:

- fully verified for all v1 browser flows
- flow complete for every route/tab/action permutation
