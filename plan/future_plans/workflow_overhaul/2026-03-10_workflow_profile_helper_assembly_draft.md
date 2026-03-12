# Workflow Profile Helper Assembly Draft

## Purpose

Describe which daemon modules would most likely assemble the future workflow-profile inspection responses and what source data each helper would consume.

This is a working-note draft for the workflow-overhaul bundle.

It is not an implementation claim.

## Goal

Tie the workflow-overhaul drafts to concrete backend assembly responsibilities:

- `NodeProfilesResponse`
- `NodeTypesResponse`
- `WorkflowBriefResponse`

## Design Direction

Do not build these responses directly inside `daemon/app.py`.

Instead:

- add helper/snapshot builders in focused daemon modules
- keep route handlers thin
- let response models be filled from those helpers

The helper layer should not invent legality at read time.

It should expose compile-frozen and daemon-derived enforcement state such as:

- decomposition-required posture
- required child-role coverage
- current blocked actions
- current-step or next-legal-step hints

This matches the repository's current backend style.

## Response-To-Helper Mapping

### `NodeProfilesResponse`

Recommended assembly home:

- new helper module or extension point near hierarchy/profile catalog code

Most likely candidates:

- extend `src/aicoding/daemon/hierarchy.py`
- or add a new `src/aicoding/daemon/workflow_profiles.py`

Recommended primary helper:

- `load_node_profiles(session_factory, resource_catalog, hierarchy_registry, *, node_id: UUID) -> NodeProfilesSnapshot`

Why this area:

- the response is mostly structural and catalog-oriented
- it depends on kind, supported/default profiles, and profile definitions

Likely source data:

- hierarchy node summary:
  - current node kind
  - tier
- node definition for that kind:
  - supported workflow profiles
  - default workflow profile
- workflow profile catalog:
  - profile ids
  - names
  - descriptions
  - main prompt refs
  - default child layout
  - required child roles

Likely current helpers or data sources to reuse:

- `get_hierarchy_node(...)`
- `load_hierarchy_registry(...)`
- future workflow-profile registry/catalog loader

### `NodeTypesResponse`

Recommended assembly home:

- hierarchy-oriented helper layer with access to profile and layout catalogs

Most likely candidates:

- extend `src/aicoding/daemon/hierarchy.py`
- use profile/layout helper functions from a future `workflow_profiles.py`

Recommended primary helper:

- `load_node_types(session_factory, resource_catalog, hierarchy_registry, *, node_id: UUID) -> NodeTypesSnapshot`

Why this area:

- the response is a richer structural/type read
- it combines hierarchy, profile, and layout compatibility information

Likely source data:

- node summary:
  - current node kind
  - tier
- node definition:
  - supported profiles
  - default profile
  - child kind constraints
- selected workflow profile if already attached to node/version/compiled context
- workflow profile definitions:
  - profile descriptors
  - child role mappings
- layout definitions:
  - compatible layouts for selected/default profile
  - role descriptions

Likely current helpers or data sources to reuse:

- `load_node_operator_summary(...)`
- `get_hierarchy_node(...)`
- future workflow-profile registry/catalog loader
- future rich-layout catalog loader

### `WorkflowBriefResponse`

Recommended assembly home:

- workflow/compiler-oriented helper layer

Most likely candidates:

- extend `src/aicoding/daemon/workflows.py`
- or add a focused `src/aicoding/daemon/workflow_briefs.py`

Recommended primary helper:

- `build_workflow_brief(session_factory, resource_catalog, hierarchy_registry, *, node_id: UUID) -> WorkflowBriefSnapshot`

Why this area:

- the response depends on selected profile, selected layout, prompt-stack composition, and recommended child profile mapping
- those are closest to compiler/runtime workflow context rather than generic hierarchy reads

Likely source data:

- node summary
- current authoritative node version
- compiled workflow context if present
- selected workflow profile
- selected layout
- node-tier prompt reference
- workflow-profile prompt reference
- brief prompt reference
- recommended child role-to-profile mapping from the selected layout/profile pair
- required repository updates
- required verification categories

Likely current helpers or data sources to reuse:

- `load_node_operator_summary(...)`
- `compile_node_workflow(...)` output conventions
- compiled workflow snapshot reads
- `resolve_effective_policy(...)` if policy influences profile or layout selection

## Recommended Snapshot Shapes

The helper layer should probably return snapshots first, then convert to daemon response models.

Suggested snapshot names:

- `NodeProfilesSnapshot`
- `NodeTypesSnapshot`
- `WorkflowBriefSnapshot`

Reason:

- this matches the current daemon style where helper layers usually return snapshot objects with `to_payload()`

## Proposed Supporting Loaders

### Workflow profile catalog loader

Recommended new helper family:

- `load_workflow_profile_catalog(resource_catalog) -> WorkflowProfileCatalogSnapshot`
- `load_workflow_profile(resource_catalog, profile_id: str) -> WorkflowProfileSnapshot`

Purpose:

- keep YAML-catalog loading and validation separate from response assembly

### Rich layout catalog loader

Recommended new helper family:

- `load_layout_catalog(resource_catalog) -> LayoutCatalogSnapshot`
- `load_layout(resource_catalog, layout_id: str) -> LayoutSnapshot`

Purpose:

- expose compatible layouts and child-role structure in one reusable place

### Profile-selection resolver

Recommended new helper:

- `resolve_node_workflow_profile(...) -> SelectedWorkflowProfileSnapshot`

Purpose:

- answer:
  - selected profile if explicit
  - default profile if implicit
  - source of selection

This same helper should feed:

- create/start flows
- materialization
- `node profiles`
- `node types`
- `workflow brief`

## Proposed Source Data Matrix

### `NodeProfilesResponse`

Needs:

- node kind
- selected profile
- supported profiles
- per-profile prompt refs
- per-profile default layout
- per-profile required child roles

### `NodeTypesResponse`

Needs:

- node kind
- selected/default profile
- supported profiles
- compatible layouts
- allowed child kinds
- child roles
- recommended child profile by role

### `WorkflowBriefResponse`

Needs:

- node kind and description
- selected profile and description
- generated objective
- prompt stack
- selected layout and description
- recommended child profiles with descriptions
- required repository updates
- required verification
- CLI discovery note

## Likely Module Ownership

### `src/aicoding/daemon/hierarchy.py`

Should likely own:

- kind-centric and hierarchy-centric reads
- reusable node-context lookup
- maybe `load_node_types(...)` if profile/layout helpers are injected cleanly

### `src/aicoding/daemon/operator_views.py`

Should likely continue owning:

- compact operator summary reads

Could be reused by:

- `node types`
- `workflow brief`

for basic node identity and current state

### `src/aicoding/daemon/workflows.py`

Should likely own:

- workflow-brief assembly
- any compile-context reads needed for profile-aware brief generation

### New `src/aicoding/daemon/workflow_profiles.py`

Recommended as the eventual home for:

- workflow profile catalog loading
- profile selection resolution
- compatibility helpers

Reason:

- keeps workflow-profile logic out of `hierarchy.py` and `workflows.py` where possible

### New `src/aicoding/daemon/layout_profiles.py` or similar

Possible eventual home for:

- richer layout catalog loading
- profile-to-layout compatibility helpers

This may be unnecessary if one compact helper module can hold both profile and layout support cleanly.

## Route Wiring Recommendation

Once helper functions exist, `daemon/app.py` routes should be thin wrappers like:

- `load_node_profiles(...)`
- `load_node_types(...)`
- `build_workflow_brief(...)`

Then wrap with:

- `NodeProfilesResponse.model_validate(snapshot.to_payload())`
- `NodeTypesResponse.model_validate(snapshot.to_payload())`
- `WorkflowBriefResponse.model_validate(snapshot.to_payload())`

## Suggested Implementation Order

1. add workflow-profile catalog loader
2. add selected-profile resolver
3. add `NodeProfilesSnapshot` and helper
4. add `NodeTypesSnapshot` and helper
5. add `WorkflowBriefSnapshot` and helper
6. wire daemon routes
7. wire CLI handlers and parser commands

## Follow-On Artifact

After this helper-assembly draft, the next useful note would be:

- a pseudo-implementation draft for the workflow-profile catalog/registry itself, including how it loads YAML, validates references, and exposes lookups to the daemon
