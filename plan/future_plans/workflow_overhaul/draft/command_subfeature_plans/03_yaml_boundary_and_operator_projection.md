# Command Foundation Plan: YAML Boundary And Operator Projection

## Parent Area

- `Command Lifecycle Foundations`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define the declarative YAML boundary and the daemon-provided CLI/website projection contract for command lifecycle state, blocked reasons, and allowed actions.

## Implementation Subtasks

- define which command properties remain declarative in YAML and which lifecycle truths must be computed only in code
- define the projection shape for CLI and website inspection so operators see shared command status, legality, and blocked-reason payloads
- define how prompt-bearing command definitions and result-routing policies align with the same lifecycle contract without creating side-channel semantics
