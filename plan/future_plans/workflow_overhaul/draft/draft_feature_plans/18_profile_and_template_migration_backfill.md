# Feature 18: Profile And Template Migration Backfill

## Goal

Backfill the workflow-profile bundle so existing authored decompositions can adopt template references safely where reuse is warranted.

## Main Work

- define migration posture for template adoption
- preserve authored one-off decomposition where reuse is not warranted
- avoid silent conversion of bespoke child structures into generated ones

## Implementation Subtasks

- define when an existing one-off decomposition may be replaced by a template reference
- define migration/backfill records for generated lineage
- document non-goals where authored decompositions should remain bespoke
- update notes and inventories so template adoption claims stay honest

## Main Dependencies

- Setup 03
- Features 08 through 14

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/db/models.py`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/inventory/major_feature_inventory.md`

## Current Gaps

- there is no migration posture for moving from one-off authored decomposition to template-driven generation
- the earlier checklist planning assumed a separate migration path for a runtime model that is now superseded
