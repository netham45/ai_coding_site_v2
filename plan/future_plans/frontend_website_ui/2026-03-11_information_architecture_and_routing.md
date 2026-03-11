# Frontend Website UI Information Architecture And Routing

## Purpose

Define the proposed structure of the website application before implementation begins.

This note focuses on:

- app shell structure
- route structure
- URL behavior
- breadcrumb behavior
- major UI regions
- core component families

This is a working note, not an implementation plan.

## Main Recommendation

The website should use a persistent application shell plus a real client-side router.

It should not be:

- a single route with hidden local state only
- a pile of unrelated full-page screens with no shared shell

The strongest shape is:

- one persistent app shell
- one persistent project/context bar
- one persistent hierarchy sidebar
- one route-driven main content panel
- tabbed detail views within the selected-node route

## App Shell

The default shell should stay stable across most operator flows.

### Shell regions

The shell should contain:

- top bar
- left navigation tree
- main content area
- optional right-side contextual drawer later, but not required for v1

### Top bar responsibilities

The top bar should expose:

- current project
- daemon health
- current selected node summary at a glance
- auth/session health if needed
- quick navigation back to project-level views

### Left tree responsibilities

The left tree should expose:

- current subtree
- hierarchy depth
- current selection
- rollup state
- filters

### Main content responsibilities

The main content area should expose:

- selected node details
- node tabs
- action confirmations
- raw JSON/debug escape hatch

## Route Structure

The website should use stable URLs that identify:

- project
- selected node
- active tab

### Recommended route shape

- `/projects`
- `/projects/:projectId`
- `/projects/:projectId/nodes/:nodeId`
- `/projects/:projectId/nodes/:nodeId/:tab`

### Optional route aliases

These may be useful but are not required if tab routes already work cleanly:

- `/projects/:projectId/tree`
- `/projects/:projectId/nodes/:nodeId/tree`
- `/projects/:projectId/nodes/:nodeId/workflow`
- `/projects/:projectId/nodes/:nodeId/runs`
- `/projects/:projectId/nodes/:nodeId/prompts`
- `/projects/:projectId/nodes/:nodeId/summaries`
- `/projects/:projectId/nodes/:nodeId/sessions`
- `/projects/:projectId/nodes/:nodeId/provenance`
- `/projects/:projectId/nodes/:nodeId/actions`

### Route meaning

Route segments should mean:

- `projectId`: selected source repo / project context exposed by the daemon, likely backed by a directory under `repos/` for the website flow
- `nodeId`: selected logical node
- `tab`: current detail tab inside the selected node

## URL Rules

URLs should be treated as durable operator state, not cosmetic detail.

### Required URL behavior

- refreshing the page should preserve selected project
- refreshing the page should preserve selected node
- refreshing the page should preserve selected tab
- using browser back/forward should restore navigation state correctly
- copying a URL should reopen the same operator view for another session on the same daemon context

### URL state that should not be required

The URL should not need to encode every piece of transient UI state.

The following may remain local or query-param based later:

- tree expansion state
- temporary filter chips
- open dialogs
- unsaved prompt edits

### Query parameter guidance

Use query params only when they materially improve sharable inspection state, such as:

- filter state worth sharing
- raw-json mode
- debug mode

Do not overuse query params for incidental UI bookkeeping.

## Breadcrumbs

The website should support both route breadcrumbs and hierarchy breadcrumbs.

### Route breadcrumbs

Route breadcrumbs should reflect application navigation, for example:

- Projects
- project_alpha
- Node
- Implementation Phase
- Prompts

### Hierarchy breadcrumbs

Hierarchy breadcrumbs should reflect actual node ancestry, for example:

- Epic A
- Phase B
- Plan C
- Task D

### Breadcrumb rule

Hierarchy breadcrumbs are more important than route breadcrumbs for operator cognition.

The route is about location in the app.

The hierarchy breadcrumb is about location in the workflow tree.

The UI should show both when useful.

## Page Families

The app should be structured around a small number of page families rather than one page per small concept.

### 1. Project index family

Purpose:

- select project
- inspect daemon/project-level readiness
- choose which source repo directory under `repos/` to start from in the website flow

Likely route:

- `/projects`

### 2. Project explorer family

Purpose:

- browse the node tree inside one project
- inspect one selected node in context

Likely route:

- `/projects/:projectId`
- `/projects/:projectId/nodes/:nodeId`
- `/projects/:projectId/nodes/:nodeId/:tab`

### 3. Optional focused views later

Purpose:

- open a specific panel in a larger or more dedicated layout if needed

These are not required for v1.

## Major UI Regions

The explorer family should have a stable visual structure.

### Region 1: project context header

Should show:

- project name
- repo path or repo identity
- daemon health
- refresh control

### Region 2: hierarchy navigator

Should show:

- tree nodes
- status rollups
- filters
- current selection

### Region 3: selected node detail

Should show:

- node title and summary
- active status
- tabs
- tab body

### Region 4: transient dialogs

Should handle:

- prompt update confirmation
- action confirmations
- failure or conflict warnings

Prompt editing should still prefer inline footer confirmation rather than modal-first UX.

## Component Taxonomy

The website should define reusable component families early so the UI does not drift page by page.

### Shell components

- `AppShell`
- `TopBar`
- `ProjectContextBar`
- `BreadcrumbBar`
- `MainLayout`

### Navigation components

- `ProjectSelector`
- `TreePanel`
- `TreeToolbar`
- `TreeNodeRow`
- `HierarchyBreadcrumbs`

### Detail components

- `NodeHeader`
- `NodeSummaryCard`
- `NodeTabs`
- `OverviewPanel`
- `WorkflowPanel`
- `RunsPanel`
- `PromptsPanel`
- `SummariesPanel`
- `SessionsPanel`
- `ProvenancePanel`
- `ActionsPanel`

### Prompt-flow components

- `PromptEditor`
- `PromptHistoryList`
- `PromptRecordViewer`
- `PromptRegenerateConfirmDialog`

### Workflow and run components

- `WorkflowStageList`
- `RunSummaryCard`
- `RunHistoryList`
- `SubtaskList`
- `SubtaskAttemptList`

### Shared state-display components

- `StatusBadge`
- `RollupBadgeGroup`
- `TimestampField`
- `KeyValueGrid`
- `JsonViewer`
- `EmptyState`
- `LoadingState`
- `ErrorState`

### Action components

- `ActionGroup`
- `ActionButton`
- `ActionReasonText`
- `ConfirmationDialog`
- `MutationResultBanner`

## Node Detail Tab Structure

The selected node route should default into a tabbed layout.

### Recommended v1 tabs

- `overview`
- `workflow`
- `runs`
- `prompts`
- `summaries`
- `sessions`
- `provenance`
- `actions`
- optional `raw`

### Tab URL rule

The active tab should be reflected in the route, not only local component state.

### Tab loading rule

Heavy tabs should fetch on demand.

The website should not load every detail payload just because a node was selected.

## Tree Interaction Model

The tree should be a navigation system first.

### Tree interaction rules

- clicking a node selects it
- selected node updates the main route
- expanding a node should not discard current detail state
- changing tabs should not collapse the tree

### Tree expansion rule

Expansion state should usually remain local to the current browser session unless later sharing needs justify URL encoding.

## Raw JSON And Debug Surfaces

The website should present data in operator-friendly form first.

### Raw tab recommendation

A raw JSON view is useful, but should be:

- optional
- clearly secondary
- aligned with the exact daemon payload actually used

### Raw tab purpose

The raw view exists to:

- help debugging
- support operator trust
- support parity checks during implementation

It should not become the primary user experience.

## Routing Consistency Rules

The frontend should adopt these consistency rules up front.

### Rule 1

Project context is always present in the route once a project is selected.

### Rule 2

Node context is always present in the route when a node detail panel is shown.

### Rule 3

The active tab is route-driven.

### Rule 4

Breadcrumbs must remain consistent with both route context and hierarchy context.

### Rule 5

The same route should always produce the same visible page family, not different layouts depending on local hidden state.

### Rule 6

For the website, project selection should come from daemon-exposed source repos rather than frontend filesystem discovery.

## Open Structural Questions

These are the main remaining structural questions after this note.

### Question 1

Should a dedicated project-level merge-back view later live under the root-node route or its own project-scoped route family?

### Question 2

Should the later merge-back flow open inline in the explorer shell or as a focused project-level screen?

### Question 3

Should a later code-server/editor route open embedded in-app or in a separate browser tab?

## Later Route Family: Top-Level Merge Back To Base Repo

The website should reserve room for a later operator flow that merges the top-level parent branch back into the selected source repo.

### Candidate route shape

- `/projects/:projectId/merge-base`
- `/projects/:projectId/nodes/:nodeId/merge-base`

### Purpose

This route family would let the operator inspect and trigger the later merge-back operation from the top-level parent into the selected base repo.

### Likely contents

- source repo identity
- base branch target
- top-level parent branch identity
- merge readiness summary
- blocking legality reasons
- merge-back confirmation surface
- durable result summary

### Scope rule

This should be limited to project/root-node contexts and should not be presented as a generic descendant-node action.

## V2 Structural Extension

One plausible v2 extension is a route family for node-scoped editor sessions.

### Candidate route shape

- `/projects/:projectId/nodes/:nodeId/editor`

### Purpose

This route would allow an operator to open a code-server or in-browser VS Code session rooted in the selected node's working directory.

### Constraints

This should remain:

- operator-only
- node-scoped
- clearly separate from the main orchestration detail tabs

It should not be treated as part of the v1 explorer shell.
