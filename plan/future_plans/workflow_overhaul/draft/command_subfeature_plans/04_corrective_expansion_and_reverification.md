# Command Foundation Plan: Corrective Expansion And Reverification

## Parent Area

- `Command Lifecycle Foundations`

## Parent Slice

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`

## Goal

Define the daemon-owned corrective-expansion contract that turns verification findings into deterministic remediation plus reverification work without mutating prior workflow history in place.

## Implementation Subtasks

- define `needs_remediation` as a first-class lifecycle outcome distinct from generic failure
- define the leaf-node contract that appends exactly one remediation subtask plus one follow-up verification or re-review subtask to the current chain
- define the non-leaf contract that materializes bounded corrective task or plan descendants and then schedules a follow-up reverification step at the current node
- define remediation-turn counters, hard loop caps, and escalation behavior when the cap is exhausted
- define finding linkage, loop-family identity, duplicate-loop prevention, and operator inspection payloads for corrective expansion
