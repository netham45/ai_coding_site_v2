# Feature 16: Checklist E2E And Flow Adoption

## Goal

Prove checklist execution mode through real runtime narratives and promote checklist-specific flows when they become operator-relevant.

## Main Work

- add real checklist-mode E2E coverage
- prove one-item-at-a-time execution
- prove blocked persistence, unblock, and `not_applicable`
- promote checklist future flows into canonical flow surfaces when warranted

## Implementation Subtasks

- implement real E2E coverage for active-item execution, blocked persistence, and `not_applicable` handling
- prove recovery and restart behavior for active and blocked checklist items
- add operator inspection E2E coverage for checklist state across CLI and website surfaces where applicable
- promote checklist future-flow drafts into canonical flow and relevant-flow inventory artifacts once runtime behavior is real

## Main Dependencies

- Setup 03
- Features 08 through 15

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `08_handle_failure_and_escalate_flow`
- `13_human_gate_and_intervention_flow`
- future checklist flows

## Relevant Current Code

- `tests/e2e/`
- `tests/unit/test_flow_e2e_alignment_docs.py`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- there are no checklist-specific real E2E routes, browser tests, or canonical flow entries
- checklist future flows are still draft-only and have not been promoted into the main flow and traceability surfaces
