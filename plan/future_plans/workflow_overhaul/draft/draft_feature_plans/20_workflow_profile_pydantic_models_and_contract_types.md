# Feature 20: Workflow-Profile Pydantic Models And Contract Types

## Goal

Add the typed request and response model work needed to make workflow-profile contracts explicit in code rather than implicit in notes.

## Main Work

- add typed request and response models for workflow-profile selection, inspection, and blocked-action contracts
- align daemon validation, CLI serialization, and website client typing around the same model family
- keep profile-aware contracts out of anonymous dict payloads

## Implementation Subtasks

- define Pydantic models for workflow-profile startup/create requests and profile-aware inspect responses
- add typed models for blocked mutation payloads, child-role coverage status, and `workflow_brief` inspection
- align daemon route handlers and helper layers to use the new models instead of ad hoc dictionaries
- document and test model serialization expectations for CLI/API and browser consumers

## Main Dependencies

- Setup 01
- Setup 02
- Feature 19

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/daemon/app.py`
- `src/aicoding/yaml_schemas.py`
- `src/aicoding/db/models.py`
- `frontend/src/lib/api/types.js`

## Current Gaps

- the future-plan bundle has a model draft note, but there was no executable draft slice for adopting those typed contracts
- current workflow-profile planning work references typed surfaces that do not yet exist in the daemon or frontend client layer
