# Feature 17: Workflow-Profile Website UI Support

## Goal

Render workflow-profile state and bounded workflow-profile actions in the website UI.

## Main Work

- add website views for selected profile, supported profiles, and `workflow brief`
- add browser support for profile-aware startup/create
- keep browser-visible state aligned with daemon-owned profile inspection surfaces

## Implementation Subtasks

- add website views for selected profile, supported profiles, compatible types/layouts, and `workflow brief`
- add browser creation/startup support for selecting `workflow_profile` where the daemon contract allows it
- render blocked reasons and legality feedback from profile-aware daemon responses without inventing browser authority
- keep browser invalidation, refresh, and navigation aligned with daemon-owned profile inspection and mutation surfaces

## Main Dependencies

- Setup 02
- Feature 02
- Feature 04
- Feature 05
- Feature 06

## Flows Touched

- website operator surfaces
- `01_create_top_level_node_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `frontend/src/components/detail/NodeDetailTabs.js`
- `frontend/src/lib/api/topLevelCreation.js`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/workflows.js`
- `frontend/src/lib/api/nodes.js`
- `frontend/src/routes/router.js`
- `frontend/src/routes/pages.js`
- `src/aicoding/daemon/app.py`

## Current Gaps

- the current website has no workflow-profile-specific views, selectors, or daemon-backed inspection surfaces
- `2026-03-12_web_ui_integration_plan.md` existed as a supporting note, but there was no executable draft feature slice for this work
