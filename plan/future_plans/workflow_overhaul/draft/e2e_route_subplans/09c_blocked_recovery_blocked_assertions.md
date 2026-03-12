# Workflow Overhaul E2E Route Subplan 09c: Blocked Recovery Blocked Assertions

## Parent Route

- `09 Blocked Recovery And Resume`

## Parent Slice

- `e2e_route_plans/09_blocked_recovery_and_resume.md`

## Goal

Define the blocked and adversarial assertions for recovery and resume.

## Implementation Subtasks

- assert recovery fails clearly when durable recovery truth is missing
- assert stale or partial recovery state is surfaced explicitly
- assert inspection still explains why resume cannot proceed
