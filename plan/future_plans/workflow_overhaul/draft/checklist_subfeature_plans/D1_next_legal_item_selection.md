# Checklist Subfeature Plan D1: Next Legal Item Selection

## Parent Area

- `D Orchestrator Loop Support`

## Parent Slice

- `draft_feature_plans/11_checklist_orchestrator_loop_support.md`

## Goal

Select the next legal checklist item deterministically.

## Implementation Subtasks

- define next-item selection from dependency and status state
- define precedence between pending, blocked, and re-evaluable items
- keep selection logic reusable across daemon and recovery paths
