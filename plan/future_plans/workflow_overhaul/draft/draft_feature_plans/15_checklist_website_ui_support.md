# Feature 15: Checklist Website UI Support

## Goal

Render checklist state and bounded checklist actions in the website UI.

## Main Work

- add checklist list/detail views
- render active item and blocker state
- expose bounded item actions backed by daemon legality

## Implementation Subtasks

- add website checklist summary and active-item detail views
- render blocker details, unblock conditions, and `not_applicable` reasons clearly
- expose bounded checklist actions that call daemon-owned legality surfaces
- keep browser state synchronized with daemon-owned checklist truth after item mutations

## Main Dependencies

- Setup 02
- Feature 10
- Feature 13
- Feature 14

## Flows Touched

- website operator surfaces
- future flow `inspect_checklist_state`
- future flow `unblock_or_mark_not_applicable`

## Relevant Current Code

- `frontend/src/components/detail/NodeDetailTabs.js`
- `frontend/src/lib/api/workflows.js`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/actions.js`
- `frontend/src/routes/router.js`

## Current Gaps

- there is no checklist UI, checklist API wrapper, or checklist detail route in the current website
- current browser surfaces cannot render blocker or `not_applicable` checklist state because no backend contract exists
