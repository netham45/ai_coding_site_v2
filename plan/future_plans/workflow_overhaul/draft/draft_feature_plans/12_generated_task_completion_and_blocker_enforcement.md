# Feature 12: Generated Task Completion And Blocker Enforcement

## Goal

Make generated tasks behave under the same blocker, completion, retry, and dependency rules as other tasks while preserving template provenance.

## Main Work

- align generated tasks with normal completion validation
- ensure dependency readiness works across generated siblings
- define recompile and drift rules for generated children

## Implementation Subtasks

- validate generated-task completion through ordinary task result registration
- ensure blocked generated tasks participate in ordinary dependency readiness
- define what happens when a template changes after children already exist
- reject hidden shortcut paths that bypass normal task authority because the task came from a template

## Main Dependencies

- Setup 02
- Feature 10
- Feature 11

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `07_pause_resume_and_recover_flow`
- `10_regenerate_and_rectify_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/workflow_events.py`
- `src/aicoding/db/models.py`

## Current Gaps

- the current future-plan bundle does not define generated-task drift or recompile posture
- the superseded checklist direction assumed item-specific completion and blocker semantics instead of normal task semantics
