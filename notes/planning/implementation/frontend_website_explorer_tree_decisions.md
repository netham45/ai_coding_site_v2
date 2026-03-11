# Frontend Website Explorer Tree Decisions

## Summary

Web feature `01_explorer_shell_and_hierarchy_tree` now ships the first real explorer shell for the website.

## Decisions

### 1. Project bootstrap is a dedicated daemon read model

- the daemon now exposes `GET /api/projects/{project_id}/bootstrap`
- this response returns:
  - the selected project entry
  - the current root node id for that project, if one exists
  - a route hint to the root overview route when a root exists

### 2. Website project-to-root linkage is recorded through workflow events

- project-scoped top-level creation now records a `website_project / top_level_created` workflow event
- the event payload stores:
  - `project_id`
  - `source_path`
- project bootstrap resolves the latest top-level root for a project by reading those durable workflow events

This keeps the website feature inside existing durable tables instead of introducing a new schema in this slice.

### 3. `/projects/:projectId` auto-selects the root node when one exists

- the browser now queries project bootstrap on the project route
- if a root exists, the route redirects to:
  - `/projects/:projectId/nodes/:nodeId/overview`
- if no root exists, the project route stays on the top-level creation view

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
- the sidebar now supports:
  - text filtering
  - lifecycle filtering
  - kind filtering
  - blocked-only filtering
  - active-only filtering
- tree links preserve the active tab where possible
- selected-node highlighting follows the route params

### 6. Tree filters are client-side over the expanded tree payload

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

## Testing

This slice was verified with:

- daemon unit and integration coverage for expanded tree payloads
- daemon integration coverage for project bootstrap root resolution
- bounded frontend checks for the explorer sidebar and full filter panel
- production build proof
- Playwright browser proof for:
  - create-node redirect
  - root auto-open
  - tree filter behavior for text, lifecycle, kind, blocked-only, and active-only
  - tree-node route navigation

## Remaining Gaps

- the main detail tabs are still placeholders and belong to later website feature phases
- project-to-root linkage is currently website-scoped via workflow events rather than a broader cross-surface project identity model
