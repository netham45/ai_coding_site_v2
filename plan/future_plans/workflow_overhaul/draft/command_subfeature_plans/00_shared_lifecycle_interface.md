# Command Foundation Plan: Shared Lifecycle Interface

## Parent Area

- `Command Lifecycle Foundations`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define the abstract daemon-owned command handler interface that every executable command kind and aligned action surface must implement or project through.

## Implementation Subtasks

- define the canonical handler methods for status inspection, allowed-action projection, begin, complete, fail, retry, and cancel semantics
- define the contract boundaries between compiled command definition data, runtime context, and durable mutation authority
- document which adjacent non-subtask action surfaces must implement the same interface directly versus adapt into it
