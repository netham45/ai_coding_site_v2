# Feature 13: Checklist Item Completion And Blocker Enforcement

## Goal

Validate checklist item terminal results against structured completion, blocker, and `not_applicable` rules.

## Main Work

- validate `completed` against structured completion predicates
- validate `blocked` against blocker schema
- validate `not_applicable` decisions against template rules

## Implementation Subtasks

- enforce completion-predicate validation before accepting `completed`
- enforce blocker-shape validation before accepting `blocked`
- enforce template and dependency rules before accepting `not_applicable`
- surface rejected terminal item results with concrete blocked or invalid-result errors

## Main Dependencies

- Setup 02
- Feature 10
- Feature 11
- Feature 12

## Flows Touched

- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `08_handle_failure_and_escalate_flow`
- future flow `unblock_or_mark_not_applicable`

## Relevant Current Code

- `src/aicoding/daemon/actions.py`
- `src/aicoding/daemon/interventions.py`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/errors.py`

## Current Gaps

- there is no checklist terminal-result validator for `completed`, `blocked`, or `not_applicable`
- current blocked-state handling is dependency and reconciliation oriented, not checklist-item oriented
