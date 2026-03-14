# Command Subfeature Plan: `recover_cursor`

## Parent Area

- `Recovery And Session Command Handlers`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define the unified lifecycle handler contract for cursor-recovery commands.

## Implementation Subtasks

- define begin/complete/fail legality for cursor recovery
- define structured recovery result payloads and recommended-action alignment
- align cursor recovery semantics with pause, session, and restart-safe behavior
