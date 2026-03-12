# Feature 11: Checklist Orchestrator Loop Support

## Goal

Run one checklist item at a time and return control to the orchestrator after each terminal item result.

## Main Work

- activate next legal item
- enforce dependency ordering
- prevent multi-item self-advancement
- handle `completed`, `blocked`, `failed`, and `not_applicable`

## Implementation Subtasks

- implement next-legal-item selection based on dependency satisfaction and terminal item states
- ensure only one checklist item is active at a time
- prevent workers from self-advancing across multiple checklist items in one turn
- hand control back to the orchestrator after `completed`, `blocked`, `failed`, or `not_applicable`

## Main Dependencies

- Setup 02
- Feature 09
- Feature 10

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- future flow `execute_checklist_item`

## Relevant Current Code

- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/admission.py`
- `src/aicoding/daemon/session_records.py`
- `src/aicoding/daemon/models.py`

## Current Gaps

- current orchestration advances compiled subtasks, not checklist items
- there is no daemon-owned single-active-checklist-item invariant or orchestrator handoff contract
