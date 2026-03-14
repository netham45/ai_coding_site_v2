# Command Foundation Plan: Handler Registry And Runtime Dispatch

## Parent Area

- `Command Lifecycle Foundations`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define how compiled command kinds resolve to shared handlers so runtime dispatch, legality checks, and mutation execution all flow through one registry-backed path.

## Implementation Subtasks

- define the registry that maps built-in command kinds and aligned action surfaces to concrete lifecycle handlers
- define how task/subtask compilation records enough command metadata for registry-backed runtime dispatch without pushing live logic into YAML
- define the migration constraints for replacing existing ad hoc dispatch paths in the daemon and intervention surfaces
