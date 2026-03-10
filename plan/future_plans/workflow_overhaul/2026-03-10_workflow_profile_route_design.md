# Workflow Profile Route Design

## Purpose

Map the workflow-profile response and pseudo-model drafts onto a likely future route and CLI design.

This is a working-note draft for the workflow-overhaul bundle.

It is not an adopted implementation plan.

## Goal

Define:

- which daemon routes would likely be added or extended
- which CLI parser entries would likely be added or extended
- which CLI handlers would likely map to those routes

## Existing Reference Points

The current implementation already has useful anchors:

- `GET /api/node-kinds`
- `POST /api/workflows/start`
- `POST /api/nodes/create`
- `node kinds`
- `node create`
- `workflow start`

These should be extended where appropriate rather than replaced wholesale.

## Proposed Daemon Routes

### `GET /api/nodes/{node_id}/types`

Proposed response model:

- `NodeTypesResponse`

Purpose:

- broader structural/type catalog for the current node context

Likely daemon responsibility:

- assemble selected profile, default profile, supported profiles, compatible layouts, allowed child kinds, and child role descriptors

### `GET /api/nodes/{node_id}/profiles`

Proposed response model:

- `NodeProfilesResponse`

Purpose:

- narrower profile-focused read for callers that do not need the full type/layout bundle

Likely daemon responsibility:

- assemble selected profile plus fuller per-profile detail rows

### `GET /api/nodes/{node_id}/workflow-brief`

Proposed response model:

- `WorkflowBriefResponse`

Purpose:

- operator-facing and AI-facing recommended decomposition brief

Likely daemon responsibility:

- compose objective, prompt stack, selected layout, recommended child profiles, and CLI discovery note

### `GET /api/workflow-profiles`

Possible response model:

- `WorkflowProfileCatalogResponse`

Purpose:

- repo-wide catalog of known workflow profiles independent of one node context

Suggested use:

- admin/debugging
- authoring support
- CLI catalog view

### `GET /api/workflow-profiles/{profile_id}`

Possible response model:

- `WorkflowProfileDetailResponse`

Purpose:

- inspect one profile definition directly

## Proposed Daemon Route Extensions

### `GET /api/node-kinds`

Current use:

- kind-level catalog

Proposed options:

1. keep it thin
2. add a `--verbose` / richer payload mode later

Recommended direction:

- keep the route mostly thin
- use `GET /api/nodes/{node_id}/types` for richer per-node context

### `POST /api/workflows/start`

Proposed request additions:

- `workflow_profile`
- `layout_id` if explicit layout selection is allowed

Likely startup response behavior:

- continue returning `WorkflowStartResponse`
- optionally include compact selected-profile metadata
- avoid returning the full `WorkflowBriefResponse` by default

### `POST /api/nodes/create`

Proposed request additions:

- `workflow_profile`
- `layout_id` if supported

Likely behavior:

- allow profile-aware child/manual creation without overloading the startup flow only

## Proposed CLI Parser Additions

### Under `node`

Add:

- `node types --node <id>`
- `node profiles --node <id>`

Likely parser shape:

```text
node
  types --node <id>
  profiles --node <id>
```

### Under `workflow`

Add:

- `workflow brief --node <id>`
- `workflow profiles list`
- `workflow profiles show --profile <id>`

Likely parser shape:

```text
workflow
  brief --node <id>
  profiles list
  profiles show --profile <id>
```

### Extend existing commands

Add flags to:

- `workflow start --workflow-profile <id>`
- `workflow start --layout <id>` if supported
- `node create --workflow-profile <id>`
- `node create --layout <id>` if supported
- `node materialize-children --workflow-profile <id>`
- `node materialize-children --layout <id>`

## Proposed CLI Handlers

### New handlers

Likely additions in `src/aicoding/cli/handlers.py`:

- `handle_node_types`
- `handle_node_profiles`
- `handle_workflow_brief`
- `handle_workflow_profiles_list`
- `handle_workflow_profiles_show`

Suggested request mapping:

- `handle_node_types` -> `GET /api/nodes/{node_id}/types`
- `handle_node_profiles` -> `GET /api/nodes/{node_id}/profiles`
- `handle_workflow_brief` -> `GET /api/nodes/{node_id}/workflow-brief`
- `handle_workflow_profiles_list` -> `GET /api/workflow-profiles`
- `handle_workflow_profiles_show` -> `GET /api/workflow-profiles/{profile_id}`

### Existing handler extensions

Extend:

- `handle_node_create`
- `handle_node_materialize_children`
- `handle_workflow_start`

so they pass:

- `workflow_profile`
- `layout_id`

when those selectors are supplied by the CLI.

## Recommended Route Grouping

Use this grouping:

- node-context reads under `/api/nodes/{node_id}/...`
- profile catalog reads under `/api/workflow-profiles...`
- startup/mutation remains under existing workflow/node mutation routes

Reason:

- keeps the per-node contextual reads distinct from the repo-wide profile catalog

## Suggested Implementation Order

1. add response models
2. add daemon read helpers
3. add `GET /api/nodes/{node_id}/profiles`
4. add `GET /api/nodes/{node_id}/types`
5. add `GET /api/nodes/{node_id}/workflow-brief`
6. add profile catalog routes
7. add CLI parser and handler entries
8. extend create/start/materialize mutation selectors

## Open Questions

### Question 1

Should `workflow brief` live under:

- `workflow brief --node <id>`

or:

- `node brief --node <id>`

Current recommendation:

- keep it under `workflow` because it is a decomposition/flow view rather than a generic node summary

### Question 2

Should `workflow profiles list` expose all profiles or only active built-ins by default?

Current recommendation:

- active built-ins by default
- add wider scopes only if project-local profile adoption becomes real

### Question 3

Should `node kinds --verbose` later overlap with `node types`?

Current recommendation:

- avoid overlap
- let `node kinds` stay global and thinner
- let `node types` be the richer node-context query

## Immediate Follow-On

After this route-design note, the next useful artifact would be:

- a pseudo-helper note describing which daemon modules assemble each response:
  - hierarchy-oriented helpers for `node types`
  - profile-catalog helpers for `node profiles`
  - compiler/workflow helpers for `workflow brief`
