# Feature 26: Templated Task Generation Flow Impact And Relevant Flow Updates

## Goal

Add the canonical flow and relevant-flow inventory changes templated task generation would require once promoted beyond future-plan status.

## Main Work

- map template-driven generation to canonical flows
- define future-flow promotions
- keep the structured flow inventory aligned with the new direction

## Implementation Subtasks

- update the compile, execution, inspection, recovery, and regenerate flow docs for template-driven child generation
- add future-flow drafts for generated-child materialization and provenance inspection
- update `relevant_user_flow_inventory.yaml` when the runtime behavior becomes real
- remove checklist-specific flow claims from the active workflow-overhaul direction

## Main Dependencies

- Setup 03
- Features 09 through 16

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `10_regenerate_and_rectify_flow`

## Relevant Current Code

- `flows/`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `tests/unit/test_flow_e2e_alignment_docs.py`

## Current Gaps

- there are no template-generation flow updates in the canonical inventory
- the active future-plan bundle still references checklist-specific flow expansion that should no longer be promoted
