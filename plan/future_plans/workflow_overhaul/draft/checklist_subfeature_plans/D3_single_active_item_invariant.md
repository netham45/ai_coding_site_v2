# Checklist Subfeature Plan D3: Single Active Item Invariant

## Parent Area

- `D Orchestrator Loop Support`

## Parent Slice

- `draft_feature_plans/11_checklist_orchestrator_loop_support.md`

## Goal

Enforce the invariant that only one checklist item may be active at a time.

## Implementation Subtasks

- define the active-item invariant in daemon-owned legality terms
- reject multi-item activation and self-advancement races
- define how the invariant is defended during recovery and retry
