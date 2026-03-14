# Checklist Item Prompt Contract

## Status

Superseded by:

- `2026-03-12_generated_task_objective_contract.md`

The active direction is to enrich normal generated task prompts with template provenance and step objectives rather than introduce a checklist-item prompt family.

## Purpose

Define the future prompt contract for active checklist-item execution when a task profile is running in checklist mode.

This is a workflow-overhaul future-plan prompt-contract note.

It is not an active runtime prompt-pack contract yet.

## Core Rule

A checklist-item prompt executes exactly one checklist item.

It does not own the whole task.

After the item reaches a terminal item result, control returns to the orchestrator.

## Required Sections

### 1. `What This Is`

Must explain:

- this prompt is for one active checklist item
- the broader task still exists above it
- the worker must not silently advance to another item

### 2. `When To Use This`

Must explain when checklist mode is the right execution style.

Suggested guidance:

- use checklist mode when the task has multiple ordered steps
- use checklist mode when each step needs its own completion predicate
- use checklist mode when the orchestrator should regain control after each completed item
- use checklist mode when inspection, implementation, verification, and documentation steps must remain separately auditable

### 3. `When Not To Use This`

Must explain when checklist mode should not be used.

Suggested guidance:

- do not use checklist mode for a single bounded step with one obvious completion condition
- do not use checklist mode when decomposition into child nodes is the real required behavior
- do not use checklist mode as a replacement for open-ended exploration before the structure is known

### 4. `Overarching Task`

Must include:

- task objective
- task profile
- why this checklist exists
- reminder that the current prompt does not complete the whole task

### 5. `Current Checklist Item`

Must include:

- item id
- item kind
- title
- goal
- dependency posture
- current status before execution

### 6. `Inputs And Context`

Must include runtime-provided item inputs such as:

- required file refs
- target paths
- commands
- target surfaces
- prior item results
- blocker history if the item is being retried

### 7. `Allowed Options`

Must list the machine-allowed options for this item.

Examples:

- `inspect_files`
- `write_note`
- `run_commands`
- `record_summary`
- `mark_completed`
- `mark_blocked`
- `mark_not_applicable`

### 8. `Forbidden Actions`

Must explicitly forbid:

- starting the next checklist item
- claiming the full task is complete
- silently changing checklist order
- inventing options that are not allowed for this item
- treating `not_applicable` as a casual skip without a reason

### 9. `Completion Conditions`

Must state what must be true before `mark_completed` is honest.

This should map directly to the item's structured `completion` section.

### 10. `Blocked Or Not Applicable Rules`

Must explain:

- when to return `blocked`
- how blockers must be recorded structurally
- when `not_applicable` is legal
- that `not_applicable` requires an explicit reason

### 11. `Return Contract`

Must require one terminal result:

- `item_completed`
- `item_blocked`
- `item_failed`
- `item_not_applicable`

And must require:

- `checklist_item_id`
- `summary`
- `artifacts`
- `evidence`
- `blockers` when blocked
- `not_applicable_reason` when not applicable

## Suggested Base Prompt Shape

```md
What this is:
- You are executing one checklist item inside a larger orchestrated task.
- Complete only the active checklist item.

When to use this:
- Use checklist mode when the task has multiple ordered steps and each step needs its own durable completion check.

When not to use this:
- Do not use checklist mode for a single bounded step or when child decomposition is the required behavior.

Overarching task:
- Objective: ...
- Profile: ...

Current checklist item:
- Id: ...
- Kind: ...
- Goal: ...

Inputs and context:
- ...

Allowed options:
- ...

Forbidden actions:
- ...

Completion conditions:
- ...

Blocked or not applicable rules:
- ...

Return contract:
- Return exactly one terminal item result.
```

## Recommended Terminal Result Shape

```yaml
status: item_completed | item_blocked | item_failed | item_not_applicable
checklist_item_id: draft_route_plan
summary: Wrote the route-plan note.
artifacts:
  - type: file_written
    path: plan/future_plans/workflow_overhaul/draft/e2e_route_plans/05_blocked_completion_before_spawn.md
evidence:
  - type: file_ref
    ref: plan/future_plans/workflow_overhaul/draft/e2e_route_plans/05_blocked_completion_before_spawn.md
blockers: []
not_applicable_reason: null
```

## Prompt Safety Rule

Checklist-item prompts should be treated as bounded execution prompts, not open-ended planning prompts.

The daemon should still validate:

- item status transitions
- completion predicates
- blocker shape
- `not_applicable` legality

Prompt compliance alone should not control checklist truth.
