# Frontend Website Detail Tabs Decisions

## Summary

Web feature `02_detail_tabs` now replaces the node-tab placeholder with real route-driven read tabs for overview, workflow, runs, summaries, sessions, and provenance.

## Decisions

### 1. The first tab slice reuses existing daemon read routes directly

Current tab-to-route mapping:

- overview:
  - `GET /api/nodes/{node_id}/summary`
  - `GET /api/nodes/{node_id}/lineage`
- workflow:
  - `GET /api/nodes/{node_id}/workflow/current`
  - `GET /api/nodes/{node_id}/subtasks/current`
  - `GET /api/nodes/{node_id}/subtasks/current/prompt`
  - `GET /api/nodes/{node_id}/subtasks/current/context`
  - `GET /api/nodes/{node_id}/subtask-attempts`
  - `GET /api/subtask-attempts/{attempt_id}`
- runs:
  - `GET /api/node-runs/{node_id}`
  - `GET /api/nodes/{node_id}/runs`
- summaries:
  - `GET /api/nodes/{node_id}/summary-history`
- sessions:
  - `GET /api/nodes/{node_id}/sessions`
- provenance:
  - `GET /api/nodes/{node_id}/sources`
  - `GET /api/nodes/{node_id}/rationale`

### 2. Tabs fetch on demand

- only the active tab fetches its tab data
- the shell tree continues polling separately
- session and run tabs keep the more active polling posture
- static history tabs stay read-heavy and lighter

### 3. Raw JSON remains an escape hatch, not the main view

- each tab now has a local raw-json toggle
- the default presentation remains summarized cards and lists
- this keeps the browser flow inspectable without collapsing into CLI-style JSON by default

### 4. Workflow detail now owns the execution-inspection surface

- the workflow tab is no longer just a task-count summary
- it now renders:
  - expandable workflow tasks
  - selectable compiled subtasks
  - current execution detail for the active subtask
  - current prompt and current context associations when the daemon exposes them
  - subtask attempt history
  - on-demand selected-attempt detail
- selected attempt detail stays lazy so the workflow tab does not eagerly fetch every attempt payload on first paint
- nodes with no active subtask or run now render empty execution states rather than browser errors

### 5. Prompts remain a separate authoring surface

- the detail-tab slice does not implement prompt history or prompt editing yet
- the current tab bar intentionally covers:
  - overview
  - workflow
  - runs
  - summaries
  - sessions
  - provenance

Prompt history and the regenerate flow remain in the next planned website feature phase.

## Testing

This slice was verified with:

- bounded frontend checks for overview-tab rendering
- bounded frontend checks for workflow-tab execution detail rendering
- production build proof
- Playwright browser proof for:
  - workflow task expansion
  - current subtask inspection
  - selected attempt inspection
  - multi-tab navigation after tree selection

## Remaining Gaps

- prompt history and prompt-edit/regenerate behavior still remain in the next website feature phase
- the detail tabs still use modest summary cards rather than richer domain-specific visualizations
- provenance currently focuses on rationale and source lineage rather than deeper graph exploration
