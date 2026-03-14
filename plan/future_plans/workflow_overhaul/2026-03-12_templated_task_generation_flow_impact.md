# Templated Task Generation Flow Impact

## Purpose

Identify which existing canonical flows templated task generation would touch and what future flow surfaces it might add.

This future-plan note replaces the checklist-execution-mode flow-impact direction.

## Flows Touched

### `01_create_top_level_node_flow`

Why touched:

- startup may select one-off child authoring or a reusable task-sequence template

Likely additions:

- template selection visibility at startup
- generated-child preview or materialization metadata

### `02_compile_or_recompile_workflow_flow`

Why touched:

- compile must freeze template references, generated dependencies, and step lineage into compiled state

Likely additions:

- template-aware child materialization
- generated lineage metadata
- recompile drift handling for generated children

### `05_admit_and_execute_node_run_flow`

Why touched:

- generated children execute as normal dependent tasks

Likely additions:

- no special checklist loop
- normal dependency-driven activation among generated children

### `06_inspect_state_and_blockers_flow`

Why touched:

- operators need to inspect whether a task was authored directly or generated from a template

Likely additions:

- template provenance visibility
- step-to-task mapping
- generated dependency inspection

### `07_pause_resume_and_recover_flow`

Why touched:

- generated tasks and their template lineage must survive restart and replacement-version handling

Likely additions:

- recovery of generated lineage
- safe rematerialization or drift detection after restart

### `10_regenerate_and_rectify_flow`

Why touched:

- rectification may need to re-materialize or reconcile generated tasks after a template or profile change

Likely additions:

- template drift classification
- generated-child reconciliation policy

## Likely New Relevant Flows

If templated task generation becomes implemented and materially operator-relevant, it would likely add at least these future canonical flows:

### Future Flow A: Materialize Generated Child Tasks

Purpose:

- select a reusable task-sequence template and materialize normal child tasks

### Future Flow B: Inspect Template Provenance

Purpose:

- inspect which tasks were authored directly versus generated from a template

### Future Flow C: Reconcile Generated Tasks After Recompile

Purpose:

- handle template drift or recompilation without losing lineage honesty

## Structured Flow Inventory Impact

When templated task generation becomes real runtime behavior, the same change or immediate follow-up should update:

- `flows/*.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
