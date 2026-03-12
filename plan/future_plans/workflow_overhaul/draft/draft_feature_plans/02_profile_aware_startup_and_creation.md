# Feature 02: Profile-Aware Startup And Creation

## Goal

Allow nodes to start or be created with a selected workflow profile while preserving parentless legality rules.

## Main Work

- add profile-aware startup/create request fields
- validate top-level legality by kind and profile
- persist selected profile on node versions

## Implementation Subtasks

- add `workflow_profile` fields to startup/create request and response models
- validate that the selected profile applies to the requested kind and top-level legality rules
- persist the selected profile on node versions even when compile fails
- update CLI flags and handler wiring for profile-aware startup and creation

## Main Dependencies

- Setup 00
- Setup 02
- Feature 01

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/manual_tree.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `src/aicoding/db/models.py`
- `tests/unit/test_workflow_start.py`
- `tests/integration/test_workflow_start_flow.py`

## Current Gaps

- startup legality is still kind and hierarchy based only, with no `workflow_profile` input
- selected profile state is not persisted on node versions or returned through startup/create surfaces
