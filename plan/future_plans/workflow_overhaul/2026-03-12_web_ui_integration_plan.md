# Workflow Overhaul Web UI Integration Plan

## Purpose

Define how the workflow-overhaul future direction should connect to the website UI and the existing frontend future-plan bundle.

This is a future-plan note.

It is not an implementation claim.

## Why This Note Is Needed

The workflow-overhaul bundle predates the current website planning and frontend implementation maturity.

The browser now already has real or planned surfaces for:

- project selection
- top-level node creation
- hierarchy tree navigation
- node detail tabs
- daemon-backed API modules

But the workflow-overhaul notes still mostly describe CLI and daemon implications and do not yet explicitly say how the browser should:

- choose workflow profiles at creation time
- inspect selected profile and effective layout state
- show `workflow brief` content
- show node-context type/profile catalogs
- render role/profile context in the tree and detail views
- render blocked-step reasons and rigid workflow legality without making operators infer them from prompt text

## Existing Browser Baseline

Current implementation surfaces reviewed:

- `frontend/src/routes/router.js`
- `frontend/src/routes/pages.js`
- `frontend/src/components/shell/HierarchyTree.js`
- `frontend/src/components/detail/NodeDetailTabs.js`
- `frontend/src/lib/api/topLevelCreation.js`
- `frontend/src/lib/api/tree.js`
- `frontend/src/lib/api/workflows.js`

Current frontend posture:

- project-scoped top-level creation already exists
- the explorer shell already has stable routes for `/projects/:projectId/nodes/:nodeId/:tab`
- the tree and detail areas are already separate
- the data-access layer is already modular and query-library-backed

That means workflow-overhaul should extend the browser's existing shape, not invent a parallel browser-only UI model.

## Relationship To Existing Frontend Future Plans

This note should be read together with:

- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`

This workflow-overhaul note does not replace that bundle.

It adds the missing browser-specific planning required once workflow profiles become real runtime state.

## Main Browser Impacts

### 1. Top-level creation flow must become profile-aware

The existing website top-level creation flow should gain:

- workflow-profile selection for the chosen kind
- daemon-provided valid profile options for that kind
- browser help text that explains what the selected profile changes

The existing website top-level creation flow should not gain in the first slice:

- first-class layout override at creation time

Reason:

- this should stay aligned with the startup/create contract
- profile is part of startup mode
- layout override belongs later at materialization time

### 2. Tree rows need profile and role visibility

Once workflow-profile-aware runtime state exists, the tree should eventually be able to show:

- selected profile badge or compact label
- assigned role when the node came from a role-bearing layout child
- effective status without forcing the operator into detail tabs

This should be an expansion of the existing tree response and tree rendering path, not a new browser-only tree concept.

### 3. Detail tabs need workflow-overhaul-specific panels or sections

The current detail-tabs model is already the right shell.

Workflow-overhaul adds the need for browser-visible sections for:

- selected workflow profile
- effective layout
- `workflow brief`
- required updates and verification obligations
- recommended child roles and profiles
- ancestry/profile-chain context

These can live inside:

- the overview tab for summary-level state
- the workflow tab for deeper compile and brief inspection

They do not need a brand-new page family.

### 4. The browser needs new daemon-backed read surfaces

The frontend future-plan bundle should assume that workflow-overhaul will eventually require API modules and query keys for:

- `node types`
- `node profiles`
- `workflow brief`
- workflow-profile catalog reads if the browser exposes profile docs directly

Recommended frontend module direction:

- `frontend/src/lib/api/types.js` can remain the home for `node types` and `node profiles`
- `frontend/src/lib/api/workflows.js` can own `workflow brief`
- top-level creation API helpers should accept `workflow_profile` once the mutation contract lands

### 5. Browser tests must cover the profile-aware operator narrative

Once workflow profiles become real runtime state, the web plan must add:

- bounded browser coverage for choosing a workflow profile at top-level creation
- detail-view coverage for selected profile and brief rendering
- tree coverage for profile/role summary display if those fields are exposed there
- blocked-action rendering for skipped required steps such as merge/completion before child spawn
- real browser E2E coverage for at least one profile-aware top-level start and follow-on inspection narrative

## Recommended Website Plan Additions

The existing frontend future-plan bundle should eventually grow the following explicit sub-slices or contract updates:

### A. Top-Level Creation Contract Update

Update the website top-level creation contract so it includes:

- valid workflow-profile options for the chosen kind
- selected workflow profile in request payload
- compact selected-profile metadata in success response

### B. Expanded Tree Contract Update

Update the expanded tree contract so it can carry, when available:

- selected profile id or label
- role label
- whether richer workflow-overhaul context exists in detail views

### C. Detail/Workflow Tab Contract Update

Update the detail-tab planning so it explicitly covers:

- workflow brief rendering
- selected profile rendering
- effective layout summary
- required updates and verification obligations

### D. Frontend Communication/Data-Access Update

Update the data-access note so it includes:

- `node types`
- `node profiles`
- `workflow brief`
- mutation invalidation rules after profile-aware startup/create

## Current Frontend Code Surfaces Likely To Change Later

Likely frontend files for the future implementation slices:

- `frontend/src/routes/pages.js`
- `frontend/src/components/shell/HierarchyTree.js`
- `frontend/src/components/detail/NodeDetailTabs.js`
- `frontend/src/lib/api/topLevelCreation.js`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/workflows.js`
- `frontend/src/lib/query/keys.js`

Likely daemon/API surfaces the browser will depend on:

- project-scoped top-level creation route
- workflow start route and response models
- tree route
- future `node types` route
- future `node profiles` route
- future `workflow brief` route

## Recommended Sequencing Against Workflow-Overhaul Slices

The browser work should follow the runtime slices rather than get ahead of them.

Recommended order:

1. profile-aware startup/create contract lands
2. browser creation flow adds `workflow_profile` selector
3. profile inspection routes land
4. browser detail tabs render selected profile and `workflow brief`
5. expanded tree adds profile/role summary fields where useful
6. browser E2E coverage is extended for workflow-profile narratives

## Practical Conclusion

The website does not need a separate workflow-overhaul architecture.

It needs targeted extensions to the existing browser plan family.

So the future authoritative workflow-overhaul planning should always reference the frontend future-plan bundle and treat website work as:

- required
- daemon-backed
- route-driven
- tree/detail oriented

rather than as a later optional polish pass.
