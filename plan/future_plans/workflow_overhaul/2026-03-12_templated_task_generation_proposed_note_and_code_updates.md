# Templated Task Generation Proposed Note And Code Updates

## Purpose

Record the concrete note and code updates that templated task generation would require if promoted into implementation.

This future-plan note replaces the checklist-execution-mode proposed-update bundle.

## Main Contract Changes

The implementation direction would need to introduce or revise:

- `task_sequence_schema_definition`
- `task_sequence_template`
- generated-task materialization lineage
- template provenance in compile and inspection surfaces

## Code Surfaces Likely To Change

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/db/models.py`
- `src/aicoding/cli/handlers.py`
- `frontend/src/lib/api/workflows.js`

## Note Families Likely To Change

- workflow-profile and compilation notes
- lifecycle and flow notes describing child materialization
- prompt-contract notes for generated-task objective context
- traceability and relevant-flow inventory notes
- proving notes for template-driven runtime narratives

## Main Questions To Resolve Before Implementation

- whether templates may be referenced by both plans and task-oriented profiles
- whether generation happens strictly at compile time, strictly at startup, or under both controlled paths
- how recompile handles existing generated children when the template changes
- how much instance-specific override surface is allowed without undermining reuse
- how template provenance appears in CLI and website inspection without overcomplicating the operator model
