# Feature 14: Checklist CLI And Operator Inspection

## Goal

Expose checklist state, active item, blockers, and prior results through CLI and operator read surfaces.

## Main Work

- add checklist inspection reads
- show active item and item statuses
- show blockers, unblock conditions, and `not_applicable` reasons

## Implementation Subtasks

- add daemon read models for checklist summary, active item detail, and item result history
- add CLI commands or subviews to inspect checklist state from operator surfaces
- expose structured blockers, unblock conditions, and `not_applicable` reasons in those reads
- ensure checklist reads stay consistent with compiled workflow and run-state inspection

## Main Dependencies

- Setup 02
- Feature 10
- Feature 13

## Flows Touched

- `06_inspect_state_and_blockers_flow`
- future flow `inspect_checklist_state`

## Relevant Current Code

- `src/aicoding/daemon/app.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `src/aicoding/daemon/operator_views.py`

## Current Gaps

- no daemon or CLI checklist inspection surfaces exist
- current operator inspection has no vocabulary for active checklist items, blockers, or `not_applicable`
