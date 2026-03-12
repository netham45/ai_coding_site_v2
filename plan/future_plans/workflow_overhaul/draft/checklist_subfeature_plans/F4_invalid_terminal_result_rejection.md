# Checklist Subfeature Plan F4: Invalid Terminal Result Rejection

## Parent Area

- `F Item Completion And Blocker Enforcement`

## Parent Slice

- `draft_feature_plans/13_checklist_item_completion_and_blocker_enforcement.md`

## Goal

Reject invalid checklist terminal results with stable daemon-owned errors.

## Implementation Subtasks

- define error codes for invalid completed, blocked, and `not_applicable` results
- classify schema failure versus legality failure versus stale-state failure
- keep rejection responses durable enough for later inspection
