# Flow 04: Manual Tree Edit And Reconcile

## Purpose

Allow operators to create or modify tree structure manually without causing silent conflict with layout-driven structure.

## Covers journeys

- manually create a child
- replace or edit a layout
- reconcile a hybrid manual/automatic subtree

## Entry conditions

- a parent node exists
- the operator performs a structural mutation or uploads a new authoritative layout

## Task flow

1. inspect current structural authority state for the parent
2. validate the requested manual mutation or layout replacement
3. classify resulting tree authority as manual, layout-driven, or hybrid
4. persist structural change request and source lineage
5. if hybrid conflict exists, pause automatic structural mutation
6. present reconciliation choices
7. execute the chosen reconciliation path
8. revalidate the resulting child graph
9. trigger recompile or replan where required

## Required subtasks

- `inspect_child_authority`
- `validate_manual_mutation`
- `persist_structure_change`
- `classify_authority_after_change`
- `pause_for_reconciliation_if_needed`
- `apply_reconciliation_decision`
- `revalidate_child_graph`
- `trigger_recompile_or_replan`

## Required capabilities

- `ai-tool node child create ...`
- `ai-tool layout update ...`
- child origin metadata
- authority-state tracking
- reconciliation command surface
- structural diff/preview

## Durable outputs

- updated child edges
- child-origin metadata
- authority classification
- reconciliation event history
- updated source lineage
- rebuild/replan event if required

## Failure cases that must be supported

- manual child violates parent constraints
- layout update conflicts with manual children
- reconciled structure contains invalid dependencies
- operator attempts silent overwrite of hybrid subtree

## Completion rule

The tree has one explicit structural authority state and any manual/layout conflict is resolved or durably paused for human decision.
