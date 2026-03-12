# Frontend Website Explorer Tree Decisions

## Summary

Web feature `01_explorer_shell_and_hierarchy_tree` now ships the first real explorer shell for the website.

## Decisions

### 1. Project bootstrap is a dedicated daemon read model

- the daemon now exposes `GET /api/projects/{project_id}/bootstrap`
- this response returns:
  - the selected project entry
  - the recommended current root node id for that project, if one exists
  - a route hint to the recommended root overview route when one exists
  - the current website-known top-level node catalog for that project

### 2. Website project-to-root linkage is recorded through workflow events

- project-scoped top-level creation now records a `website_project / top_level_created` workflow event
- the event payload stores:
  - `project_id`
  - `source_path`
- project bootstrap resolves the latest top-level root for a project by reading those durable workflow events

This keeps the website feature inside existing durable tables instead of introducing a new schema in this slice.

### 3. `/projects/:projectId` remains a project workspace even when roots exist

- the browser now queries project bootstrap on the project route
- the project route now stays renderable whether the project has:
  - no roots
  - one root
  - multiple roots
- the route now renders:
  - the top-level creation form
  - the existing top-level node catalog for that project
- selecting an existing top-level node is now an explicit operator navigation step rather than an unconditional redirect

### 4. The tree route is now the expanded browser contract

- `GET /api/nodes/{node_id}/tree` now returns:
  - generated timestamp
  - authoritative and latest-created version ids
  - blocker state
  - child count and `has_children`
  - immediate-child rollups
  - creation timestamp
  - last-updated timestamp

The route remains the same logical object; it is just richer now.

### 5. The shell owns tree navigation

- the persistent sidebar now renders the hierarchy tree
- when no node route is selected and the operator is on `/projects/:projectId`, the sidebar renders the project top-level node list rather than forcing one root tree
- when a node route is selected, the sidebar now resolves that node's ancestor chain and anchors the tree to the selected node's actual top-level root
- the node-route tree is now a real expandable browser tree rather than a flat indented list
- the sidebar keeps:
  - selected-node ancestor branches expanded
  - breadcrumb context for non-root selections
  - an explicit subtree-focus/reset control for narrowing the visible branch
- the sidebar now supports:
  - text filtering
  - lifecycle filtering
  - kind filtering
  - blocked-only filtering
  - active-only filtering
- tree links preserve the active tab where possible
- selected-node highlighting follows the route params

### 6. V1 tree loading remains eager, with browser-local expansion and focus state

- feature `10_expandable_tree_navigation_and_focus` keeps the current `GET /api/nodes/{node_id}/tree` full-subtree read model for v1
- expand/collapse state is browser-local and not daemon-owned
- subtree focus is browser-local and route-scoped
- this avoids introducing a second daemon read model before the real tree interaction contract is proven in browser tests
- the current tradeoff is that large trees still require eager payload delivery, so lazy child loading remains a later scalability phase if runtime data shows the current payload is too heavy

### 7. Tree filters are client-side over the expanded tree payload

- feature `07_tree_filter_completion` did not require a second tree route or new daemon query parameters
- the current expanded tree payload already exposes the fields needed for:
  - lifecycle filter
  - blocked-only filter
  - active-only filter
  - kind filter
- current shipped filter semantics are:
  - lifecycle filter: exact match on `lifecycle_state`
  - kind filter: exact match on `kind`
  - blocked-only: includes `blocked` and `paused_for_user` scheduling/blocker states
  - active-only: includes nodes currently running or already scheduled as running
- filter changes do not change the selected route; they only change which nodes are visible in the sidebar list
- when a descendant matches a filter, the browser keeps its ancestor context visible so the match remains navigable inside the tree

## Testing

This slice was verified with:

- daemon unit and integration coverage for expanded tree payloads
- daemon integration coverage for project bootstrap root resolution and top-level node catalog resolution
- bounded frontend checks for the explorer sidebar and full filter panel
- production build proof
- Playwright browser proof for:
  - create-node redirect
  - project workspace re-entry after root creation
  - explicit existing-root navigation
  - real tree expansion and collapse over a nested mock branch
  - subtree focus and reset on a selected branch
  - tree filter behavior for text, lifecycle, kind, blocked-only, and active-only while preserving ancestor context
  - tree-node route navigation

## Remaining Gaps

- the main detail tabs are still placeholders and belong to later website feature phases
- project-to-root linkage is currently website-scoped via workflow events rather than a broader cross-surface project identity model
- tree loading is still eager for v1; lazy child loading remains undecided beyond the current browser-local proof
