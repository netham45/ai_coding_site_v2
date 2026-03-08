# Flow 03: Materialize And Schedule Children

## Purpose

Convert an authoritative layout into durable child nodes and dependency edges, then classify which children are ready to run.

## Covers journeys

- auto-decompose a parent into child work
- spawn child tasks/phases/plans
- determine readiness and blocking state

## Entry conditions

- a parent node version exists
- the parent has an authoritative compiled layout or equivalent child specification

## Task flow

1. load the authoritative parent layout
2. validate child IDs, kinds, tiers, and dependency references
3. reject cycles, self-dependencies, and illegal relative dependencies
4. compare the layout against any existing materialized child set
5. if unchanged, return existing child set idempotently
6. if changed, enter explicit replan/reconciliation path rather than mutating silently
7. create child node versions and parent-child edges
8. create dependency edges
9. compile children where policy allows
10. classify each child as ready, blocked, running, complete, failed, superseded, or paused
11. auto-start ready children if parent policy enables it

## Required subtasks

- `load_authoritative_layout`
- `validate_child_specs`
- `validate_dependency_graph`
- `compare_to_existing_child_set`
- `materialize_child_nodes`
- `persist_dependency_edges`
- `compile_children_if_enabled`
- `classify_scheduling_state`
- `start_ready_children_if_enabled`

## Required capabilities

- layout validation
- parent/child constraint validation
- invalid dependency graph handling
- idempotent child materialization
- child scheduling classification
- ready-child admission/start behavior

## Durable outputs

- child node version records
- parent-child edges
- child dependency edges
- initial child statuses
- materialization summary
- scheduling classification per child

## Failure cases that must be supported

- invalid layout
- duplicate child IDs
- missing dependency targets
- dependency cycles
- hybrid tree conflict requiring reconciliation
- child compilation failure

## Completion rule

The parent can explain its child set structurally and can show exactly why each child is ready or blocked.
