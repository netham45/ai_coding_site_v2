# Feature 19: Workflow-Profile API Response Shapes And Read Models

## Goal

Turn the workflow-profile response-shape draft into explicit executable work for daemon responses, CLI consumers, and website read models.

## Main Work

- define the daemon-owned response payloads for profile-aware create, compile, inspect, and blocked-action surfaces
- align CLI and website consumers to one stable response vocabulary
- prevent profile-aware inspection surfaces from drifting into ad hoc response shapes

## Implementation Subtasks

- define the canonical response fields for selected profile, compatible profiles, effective layout, child-role coverage, blocked reasons, and `workflow_brief`
- add explicit read-model contracts for operator inspection surfaces instead of leaving profile metadata embedded in generic workflow payloads
- align CLI and website consumer expectations with the same response-shape contract
- document error payloads for blocked completion, blocked merge, and invalid profile/layout combinations

## Main Dependencies

- Setup 02
- Feature 02
- Feature 04
- Feature 05

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`
- `12_query_provenance_and_docs_flow`

## Relevant Current Code

- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/workflows.js`
- `frontend/src/lib/api/nodes.js`

## Current Gaps

- the future-plan bundle has a response-shape note, but the draft execution queue had no standalone slice for implementing those payload contracts
- current daemon and website surfaces still expose generic workflow responses rather than workflow-profile-specific read models
