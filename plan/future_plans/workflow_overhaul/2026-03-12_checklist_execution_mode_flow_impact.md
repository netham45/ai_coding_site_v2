# Checklist Execution Mode Flow Impact

## Purpose

Identify which existing canonical flows checklist execution mode would touch and what new flow surfaces it would likely add.

This is a workflow-overhaul future-plan note.

It is not a current flow-inventory update.

## Flows Touched

Checklist execution mode would directly touch these existing canonical flows.

### `01_create_top_level_node_flow`

Why touched:

- top-level startup may create a node/version configured for checklist execution mode

Likely additions:

- selected execution mode visible at startup
- initial checklist attachment visibility if present at create time

### `02_compile_or_recompile_workflow_flow`

Why touched:

- compile must freeze checklist execution mode and checklist contract inputs into compiled state

Likely additions:

- checklist-aware compiled workflow context
- item-ordering and allowed-status metadata

### `05_admit_and_execute_node_run_flow`

Why touched:

- the command loop must run one checklist item at a time

Likely additions:

- active checklist item selection
- item terminal result handling
- return-to-orchestrator after each item

### `06_inspect_state_and_blockers_flow`

Why touched:

- operators need to inspect active checklist items, item statuses, blockers, and unblock conditions

Likely additions:

- checklist item list inspection
- active item detail
- blocker detail
- `not_applicable` reason visibility

### `07_pause_resume_and_recover_flow`

Why touched:

- active checklist item state and blockers must survive interruption and restart

Likely additions:

- recovery of active item context
- blocked item persistence across restart

### `08_handle_failure_and_escalate_flow`

Why touched:

- blocked and failed checklist items become explicit runtime outcomes

Likely additions:

- item-level failure classification
- blocker-driven escalation or replan behavior

### `09_run_quality_gates_flow`

Why touched:

- some checklist items may be verification or quality-gate items with their own completion predicates

Likely additions:

- item-specific quality evidence persistence

### `10_regenerate_and_rectify_flow`

Why touched:

- checklist instances may need reevaluation, migration, or invalidation after recompile or rectification

Likely additions:

- stale item handling after rebuild
- blocker reevaluation after changed runtime state

### `13_human_gate_and_intervention_flow`

Why touched:

- blocked or `not_applicable` item decisions may require operator or human intervention in some checklist templates

Likely additions:

- explicit item-level intervention records

## Website Surfaces Touched

Checklist execution mode also touches the website operator surface, even though the canonical flow inventory does not yet split that into a separate checklist-specific flow.

Main website impacts:

- checklist list/detail rendering
- active item rendering
- blocker rendering
- bounded item actions

## Likely New Relevant Flows

If checklist execution mode becomes implemented and materially operator-relevant, it would likely add at least these future canonical flows:

### Future Flow A: Execute Checklist Item

Purpose:

- run one active checklist item and return to orchestrator

### Future Flow B: Inspect Checklist State

Purpose:

- inspect checklist items, active item, blocker state, and prior item results

### Future Flow C: Unblock Or Mark Not Applicable

Purpose:

- clear a blocked item or explicitly mark an item `not_applicable` through bounded authority surfaces

## Structured Flow Inventory Impact

When checklist mode becomes real runtime behavior, the same change or immediate follow-up should update:

- `flows/*.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`

This note does not itself promote new flows into the authoritative runtime inventory yet.
