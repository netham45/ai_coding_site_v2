# Feature 10: Durable Checklist Persistence

## Goal

Persist checklist instances, item states, blockers, results, and `not_applicable` decisions durably.

## Main Work

- add checklist persistence model
- persist active item and item history
- persist blockers and unblock conditions

## Implementation Subtasks

- add durable storage for checklist instances and item rows or equivalent instance-backed payloads
- persist active item identity, item status transitions, and terminal item results
- persist structured blockers, unblock conditions, and `not_applicable` reasons
- expose enough history to reconstruct how the checklist progressed across retries and restarts

## Main Dependencies

- Setup 02
- Feature 08
- Feature 09

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `08_handle_failure_and_escalate_flow`

## Relevant Current Code

- `src/aicoding/db/models.py`
- `src/aicoding/daemon/session_records.py`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/models.py`

## Current Gaps

- no current tables or payloads exist for checklist instances, items, blockers, or terminal item results
- recovery logic cannot reconstruct checklist state because no checklist persistence exists
