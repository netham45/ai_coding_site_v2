# Feature 18: Profile And Checklist Migration Backfill

## Goal

Add the narrower migration and backfill slice for new workflow-profile and checklist persistence.

## Main Work

- define additive migration order for selected profile, compiled profile context, and checklist persistence
- define rollout/backfill posture for pre-existing nodes and runs
- define mixed-state handling during the transition period

## Implementation Subtasks

- define the migration order for selected-profile persistence, compiled profile context, and checklist persistence structures
- define backfill posture for existing node versions, compiled workflows, and runs that predate these fields
- define mixed old/new state handling for inspection, restart, and mutation legality while rollout is incomplete
- add the proving and operator-diagnosis expectations for migration/backfill outcomes so partial rollout stays inspectable

## Main Dependencies

- Setup 02
- Feature 02
- Feature 04
- Feature 08
- Feature 10

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`

## Relevant Current Code

- `src/aicoding/db/models.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/session_records.py`
- `src/aicoding/daemon/app.py`

## Current Gaps

- the draft queue previously referenced migration/backfill needs only indirectly inside setup and persistence slices
- there is still no dedicated execution slice for rollout-safe persistence adoption across pre-existing runtime data
