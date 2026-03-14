# Checklist Execution Mode Proposed Note And Code Updates

## Status

Superseded by:

- `2026-03-12_templated_task_generation_proposed_note_and_code_updates.md`

The active direction now tracks note and code updates for task-sequence templates and generated-task provenance instead of a checklist-specific runtime.

## Purpose

Record the concrete note and code updates that checklist execution mode would require if promoted into implementation.

This is a workflow-overhaul future-plan note.

It is not an implementation claim.

## Proposed Note Updates

### `notes/specs/yaml/yaml_schemas_spec_v2.md`

Add:

- `checklist_schema_definition`
- `checklist_template_definition`
- `checklist_instance`
- execution-mode support for task-oriented workflow profiles

### `notes/specs/runtime/runtime_command_loop_spec_v2.md`

Add:

- checklist-item activation rules
- terminal item result handling
- blocked item persistence
- `not_applicable` legality
- return-to-orchestrator behavior

### `notes/specs/cli/cli_surface_spec_v2.md`

Add:

- checklist inspection commands
- active item inspection
- blocker inspection
- bounded item result submission if needed

### `notes/specs/runtime/node_lifecycle_spec_v2.md`

Add:

- how checklist mode interacts with node run state
- how active checklist items map to workflow/subtask progression

### `notes/catalogs/checklists/e2e_execution_policy.md`

Add:

- checklist-mode E2E proving expectations
- rules against synthetic item advancement

### `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`

Potential future update:

- add checklist-specific flows once they are runtime-relevant

## Proposed Code Updates

### `src/aicoding/yaml_schemas.py`

Add:

- checklist schema models
- template models
- instance models
- execution-mode fields for applicable profile or task documents

### `src/aicoding/daemon/workflows.py`

Add:

- compile-frozen checklist execution context
- checklist item order and item contract visibility

### `src/aicoding/daemon/app.py`

Add or extend:

- checklist inspection routes
- bounded checklist-item result routes if that becomes the mutation posture

### `src/aicoding/daemon/models.py`

Add:

- response models for checklist state and active item detail

### Database schema

Likely add:

- checklist instance table or equivalent durable record family
- checklist item table or JSON-backed durable structure
- blocker records
- item result history

### CLI

Likely extend:

- `node show`
- `workflow show`
- or dedicated checklist inspection commands

### Prompt assets

Add:

- checklist-item execution prompt
- checklist blocked-item retry prompt if needed
- checklist inspection/summary prompt if needed

### Website UI

Add:

- checklist detail panel
- active item display
- blocker display
- bounded item action controls

## Canonical Feature Buckets This Work Would Touch

The checklist-mode implementation would touch or extend work in at least these existing feature areas:

- workflow compilation and compiled context
- node run orchestration
- AI-facing CLI command loop
- operator inspection surfaces
- execution orchestration and result capture
- runtime-state persistence
- website operator inspection

It likely deserves its own authoritative feature-plan family once promoted.
