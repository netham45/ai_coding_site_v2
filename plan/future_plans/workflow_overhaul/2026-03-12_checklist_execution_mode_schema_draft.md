# Checklist Execution Mode Schema Draft

## Status

Superseded by:

- `2026-03-12_task_sequence_template_schema_draft.md`

The active direction is to model reusable decomposition as task-sequence templates that materialize normal child tasks, not checklist instances with their own runtime lifecycle.

## Purpose

Define a draft schema for checklist execution mode as an optional execution contract that any task-oriented workflow profile may enable.

This is a workflow-overhaul future-plan note.

It is not an adopted runtime schema.

## Core Recommendation

Checklist should not be a definitive task type.

It should be an execution mode that a task profile may opt into.

Recommended top-level shape:

```yaml
execution_mode: single_step | checklist
checklist:
  template_id: e2e_route_plan_v1
  item_ordering: sequential
  max_active_items: 1
  allow_reordering: false
  return_to_orchestrator_after_each_item: true
  require_explicit_item_completion: true
  allow_not_applicable_items: true
```

## Why Execution Mode Is Better Than A New Type

- the task remains semantically `task.implementation`, `task.docs`, `task.e2e`, or similar
- execution style stays separate from semantic role
- the same profile family can support both bounded single-step work and multi-step checklist work
- migration is easier because the runtime does not need a fake new semantic kind

## Recommended Schema Layers

Use three layers:

1. `checklist_schema_definition`
2. `checklist_template_definition`
3. `checklist_instance`

The runtime should trust the instance only after validating it against the schema and template.

## Layer 1: `checklist_schema_definition`

Purpose:

- define the shared checklist envelope
- define allowed item kinds
- define allowed status values
- define blocker shape
- define completion and result shape

Suggested shape:

```yaml
kind: checklist_schema_definition
id: checklist_schema_v1
schema_version: 1
allowed_item_statuses:
  - pending
  - in_progress
  - completed
  - blocked
  - failed
  - not_applicable
allowed_item_kinds:
  - inspect
  - implement
  - verify
  - document
  - plan
  - review
  - reconcile
  - delegate
allowed_blocker_categories:
  - dependency
  - runtime_gap
  - design_gap
  - missing_input
  - awaiting_decision
  - external_requirement
```

## Layer 2: `checklist_template_definition`

Purpose:

- define a reusable checklist family
- constrain item kinds and item ordering
- document when checklist mode should be used

Suggested shape:

```yaml
kind: checklist_template_definition
id: e2e_route_plan_v1
schema_ref: checklist_schema_v1
name: E2E Route Plan Checklist
description: Build one route plan through ordered planning steps.
when_to_use:
  - task has multiple ordered steps
  - each step needs its own durable completion predicate
  - orchestrator should regain control after each step
when_not_to_use:
  - task is single-step and bounded
  - decomposition into child nodes is the correct behavior
execution_defaults:
  item_ordering: sequential
  max_active_items: 1
  allow_reordering: false
  return_to_orchestrator_after_each_item: true
  allow_not_applicable_items: true
allowed_item_kinds:
  - inspect
  - document
  - verify
required_completion_fields:
  - required_artifacts
```

## Layer 3: `checklist_instance`

Purpose:

- attach a concrete checklist to a task or node instance
- track current status, blockers, completion results, and active item

Suggested shape:

```yaml
kind: checklist_instance
schema_version: 1
id: checklist.route_05.001
template_id: e2e_route_plan_v1
owner:
  node_id: uuid
  node_version_id: uuid
  workflow_profile_id: task.e2e
overall_goal: Prove blocked completion before spawn through a real E2E route.
overall_status: in_progress
execution:
  item_ordering: sequential
  max_active_items: 1
  allow_reordering: false
  return_to_orchestrator_after_each_item: true
  require_explicit_item_completion: true
  allow_not_applicable_items: true
active_item_id: inspect_runtime_contract
items:
  - id: inspect_runtime_contract
    kind: inspect
    title: Inspect runtime contract
    goal: Confirm the current daemon and CLI contract for blocked completion behavior.
    status: completed
    depends_on: []
    inputs:
      required_refs:
        - notes/specs/runtime/node_lifecycle_spec_v2.md
    allowed_options:
      - inspect_files
      - record_summary
      - mark_completed
      - mark_blocked
      - mark_not_applicable
    completion:
      required_artifacts:
        - summary
      required_evidence:
        - file_refs
    result:
      summary: Runtime contract inspected.
  - id: draft_route_plan
    kind: document
    title: Draft route plan
    goal: Write the route-plan note.
    status: blocked
    depends_on:
      - inspect_runtime_contract
    inputs:
      target_path: plan/future_plans/workflow_overhaul/draft/e2e_route_plans/05_blocked_completion_before_spawn.md
    allowed_options:
      - write_note
      - mark_completed
      - mark_blocked
      - mark_not_applicable
    completion:
      required_artifacts:
        - file_written
    blockers:
      - code: missing_runtime_contract
        category: dependency
        summary: Waiting on the authoritative blocked-mutation payload contract.
        unblocks_when:
          - type: note_updated
            ref: plan/future_plans/workflow_overhaul/draft/blocked_mutation_contract.md
```

## Recommended Status Vocabulary

Use these item statuses:

- `pending`
- `in_progress`
- `completed`
- `blocked`
- `failed`
- `not_applicable`

Recommended meaning:

- `pending`: not started
- `in_progress`: currently active
- `completed`: all completion predicates satisfied
- `blocked`: cannot proceed until structured blocker conditions clear
- `failed`: attempted and failed in a way that is not just waiting on an unblock condition
- `not_applicable`: deliberately ruled out for this instance with an explicit reason

`not_applicable` is better than a vague skip because it records:

- why the item does not apply
- who decided that
- what remaining items are still legal afterward

## Recommended Blocker Shape

Each blocked item should record structured blockers.

Suggested blocker shape:

```yaml
blockers:
  - code: missing_runtime_contract
    category: dependency
    summary: Waiting on the authoritative blocked-mutation payload contract.
    details:
      missing_contract: blocked_mutation_payload
      affected_surface: daemon
    unblocks_when:
      - type: note_updated
        ref: plan/future_plans/workflow_overhaul/draft/blocked_mutation_contract.md
    detected_by:
      - worker
      - orchestrator
```

Recommended blocker fields:

- `code`
- `category`
- `summary`
- `details`
- `unblocks_when`
- `detected_by`

## Recommended Item Envelope

All item kinds should share this envelope:

- `id`
- `kind`
- `title`
- `goal`
- `status`
- `depends_on`
- `inputs`
- `allowed_options`
- `completion`
- `result`
- `blockers`
- `not_applicable_reason`

The envelope is universal.

The contents of `inputs`, `completion`, and `result` should still be constrained by item kind.

## Recommended Item Kinds

Suggested starter item kinds:

- `inspect`
- `implement`
- `verify`
- `document`
- `plan`
- `review`
- `reconcile`
- `delegate`

The runtime should not allow arbitrary new item kinds to appear in instances without schema/template support.

## Recommended Kind-Specific Input Rules

Example:

```yaml
item_kind_rules:
  inspect:
    required_inputs:
      - required_refs
  verify:
    required_inputs:
      - commands
  document:
    required_inputs:
      - target_path
  implement:
    required_inputs:
      - target_surfaces
```

## Recommended Completion Shape

Suggested `completion` shape:

```yaml
completion:
  required_artifacts:
    - summary
    - file_written
  required_evidence:
    - file_refs
    - command_results
  manual_review_required: false
```

This lets the daemon decide whether an item is actually complete rather than trusting a freeform claim.

## Orchestrator Rules

The orchestrator should:

- activate at most one item at a time
- only activate an item whose dependencies are satisfied
- allow `not_applicable` only when the template permits it
- reevaluate blocked items against their `unblocks_when` data
- never let the worker advance multiple checklist items in one turn
- regain control after every `completed`, `blocked`, `failed`, or `not_applicable` result

## AI Trust Boundary

The runtime should not trust a raw AI-authored checklist as authoritative structure.

Recommended trust model:

- schema is human-authored
- template is human-authored
- instance is compiler-built or AI-assisted but daemon-validated
- item completion is daemon-validated against structured predicates

That keeps checklist mode flexible without letting runtime AI invent unconstrained workflow structure.
