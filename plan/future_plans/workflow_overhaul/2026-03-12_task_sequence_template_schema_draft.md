# Task Sequence Template Schema Draft

## Purpose

Define a draft schema direction for reusable task-sequence templates that materialize normal child tasks.

This future-plan note replaces the earlier checklist-instance draft.

It is not an adopted runtime schema.

## Core Recommendation

Represent reusable decomposition as a template family, not as a second execution mode.

Recommended top-level shape:

```yaml
kind: task_sequence_template
id: e2e_route_v1
applies_to_profiles:
  - task.e2e
materialization:
  strategy: spawn_child_tasks
  freeze_dependencies_at_compile: true
  allow_instance_overrides: false
steps:
  - id: inspect_contract
    title: Inspect runtime contract
    objective: Confirm the daemon and CLI contract for the route.
    task_profile: task.docs
    depends_on: []
  - id: prove_real_e2e
    title: Prove real E2E
    objective: Add and run the route's real E2E proof.
    task_profile: task.e2e
    depends_on:
      - inspect_contract
```

## Main Layers

Use three layers:

1. `task_sequence_schema_definition`
2. `task_sequence_template`
3. `generated_task_materialization_record`

The first two are authoring assets.

The third is durable runtime evidence showing which normal tasks were generated from the template.

## Layer 1: `task_sequence_schema_definition`

Purpose:

- define the shared template envelope
- define allowed step fields
- define dependency rules
- define allowed objective/context fields

Suggested shape:

```yaml
kind: task_sequence_schema_definition
id: task_sequence_schema_v1
schema_version: 1
allowed_step_fields:
  - id
  - title
  - objective
  - task_profile
  - depends_on
  - required_context
  - expected_outputs
  - proving_targets
allowed_materialization_strategies:
  - spawn_child_tasks
```

## Layer 2: `task_sequence_template`

Purpose:

- define a reusable sequence of normal tasks
- encode step dependencies and objectives
- document when the template should be used instead of one-off authoring

Suggested shape:

```yaml
kind: task_sequence_template
id: feature_delivery_v1
schema_ref: task_sequence_schema_v1
name: Feature Delivery Sequence
description: Materialize the standard implementation to proving ladder.
when_to_use:
  - a recurring decomposition already exists
  - the same proving ladder should be reused
when_not_to_use:
  - the child tasks are bespoke to one plan
  - author-directed decomposition is itself the work product
materialization:
  strategy: spawn_child_tasks
  freeze_dependencies_at_compile: true
  allow_instance_overrides: false
steps:
  - id: implement_change
    task_profile: task.implementation
    depends_on: []
  - id: update_notes
    task_profile: task.docs
    depends_on:
      - implement_change
  - id: prove_e2e
    task_profile: task.e2e
    depends_on:
      - update_notes
```

## Layer 3: `generated_task_materialization_record`

Purpose:

- record which template created which child tasks
- preserve step-to-task lineage for inspection and audit
- allow recompile or backfill logic to detect drift

Suggested shape:

```yaml
kind: generated_task_materialization_record
schema_version: 1
template_id: feature_delivery_v1
owner:
  node_id: uuid
  node_version_id: uuid
generated_tasks:
  - step_id: implement_change
    child_node_id: uuid
    child_node_version_id: uuid
  - step_id: update_notes
    child_node_id: uuid
    child_node_version_id: uuid
```

## Recommended Rules

- templates may define task objectives and dependency structure
- templates should not create a second task lifecycle
- generated tasks should use the same durable state and run semantics as authored tasks
- the compiler should freeze the generated dependency graph into normal compiled workflow state
- prompt delivery should remain task-oriented, not template-item-oriented

## Main Decision Boundary

Use a template when the value is reuse and policy consistency.

Use one-off authored child tasks when the value is bespoke decomposition.
