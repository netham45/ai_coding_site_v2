# Workflow Overhaul E2E Route Subplan 08b: Parent Merge Happy Path

## Parent Route

- `08 Parent Merge Narrowness`

## Parent Slice

- `e2e_route_plans/08_parent_merge_narrowness.md`

## Goal

Define the happy-path assertions for narrow parent merge behavior.

## Implementation Subtasks

- assert the parent may perform only allowed reconciliation actions
- assert merge consumes descendant outputs without absorbing child-owned implementation
- assert parent summary and merge state remain inspectable
