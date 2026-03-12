# Workflow Overhaul E2E Route Subplan 00c: Blocked Start Assertions

## Parent Route

- `00 Parentless Profile Start`

## Parent Slice

- `e2e_route_plans/00_parentless_profile_start.md`

## Goal

Define the blocked-path assertions for illegal parentless startup attempts.

## Implementation Subtasks

- assert rejection for unsupported kind/profile pairs
- assert rejection for non-parentless kinds started at the top level
- assert blocked reasons remain concrete and inspectable
