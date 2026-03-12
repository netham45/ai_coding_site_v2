# Workflow Overhaul E2E Route Subplan 05b: Completion Before Spawn Happy Path

## Parent Route

- `05 Blocked Completion Before Spawn`

## Parent Slice

- `e2e_route_plans/05_blocked_completion_before_spawn.md`

## Goal

Define the positive assertions for the blocked-completion-before-spawn route.

## Implementation Subtasks

- assert the route reaches the illegal completion attempt through real runtime state
- assert the blocked response returns the expected machine-readable code
- assert no silent completion or merge occurs
