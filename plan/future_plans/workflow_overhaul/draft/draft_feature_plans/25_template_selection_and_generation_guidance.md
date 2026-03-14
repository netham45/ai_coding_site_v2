# Feature 25: Template Selection And Generation Guidance

## Goal

Make the templated-task-generation overview executable by defining when reusable generation should be chosen instead of one-off authored decomposition.

## Main Work

- define selection guidance for template use
- align profile-level support, plan-level authoring, and operator understanding
- prevent templates from becoming a vague catch-all replacement for normal planning

## Implementation Subtasks

- define when a recurring sequence should be modeled as a reusable template
- define when a decomposition should remain bespoke and authored directly in the plan
- document selection guidance for orchestrator and operator choice
- document rollout boundaries, limitations, and non-goals for the first template-generation wave

## Main Dependencies

- Setup 00
- Feature 08
- Feature 09

## Flows Touched

- `01_create_top_level_node_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`

## Current Gaps

- current planning does not define when template-driven generation is preferable to one-off child authoring
- the earlier checklist rollout guidance no longer matches the preferred runtime model
