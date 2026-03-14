# Command Foundation Plan: State, Legality, And Action Result Models

## Parent Area

- `Command Lifecycle Foundations`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define the shared command state vocabulary and the structured legality/result payloads that all command handlers must use.

## Implementation Subtasks

- define the canonical command state enum and the invariants for pending, ready, running, blocked, completed, failed, and cancelled states
- define structured legality payloads with code, summary, and machine-readable details for blocked and rejected actions
- define structured action-result payloads for accepted transitions, next actions, output payloads, and durable audit projection
