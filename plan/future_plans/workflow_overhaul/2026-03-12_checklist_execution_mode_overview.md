# Checklist Execution Mode Overview

## Status

Superseded by:

- `2026-03-12_templated_task_generation_overview.md`
- `2026-03-12_task_sequence_template_schema_draft.md`

The repository direction is now:

- templated task generation for reusable decomposition
- one-off authored child tasks for bespoke decomposition

There is no longer an active proposal to add a separate checklist runtime.

## Purpose

Capture the intended role of checklist execution mode inside the workflow-overhaul direction.

This is a future-plan note.

It is not an implementation claim.

## Core Position

Checklist is not a new semantic task type.

It is an optional execution mode that a task-oriented workflow profile may enable when the work is:

- multi-step
- ordered
- separately auditable per step
- better run one item at a time with control returning to the orchestrator after each item

Recommended posture:

- semantic profile stays the same
- execution mode changes from `single_step` to `checklist`

Example:

- `task.e2e` may run as `single_step`
- `task.e2e` may also run as `checklist` when proving a longer route or implementation-ready plan sequence

## Why This Exists

This mode addresses a recurring failure pattern:

- one node is given too much multi-step work
- the worker informally manages a mental checklist
- intermediate states are not durable enough
- the worker can skip, collapse, or over-complete steps

Checklist mode fixes that by making the intermediate work explicit and daemon-visible.

## What Checklist Mode Adds

Checklist mode adds:

- a structured checklist instance attached to the task
- one active checklist item at a time
- structured item statuses
- structured blockers with unblock conditions
- explicit `not_applicable` handling
- a dedicated active-item prompt contract
- mandatory return to orchestrator after each item result

## Recommended Status Model

Checklist item statuses should be:

- `pending`
- `in_progress`
- `completed`
- `blocked`
- `failed`
- `not_applicable`

`not_applicable` is preferred over a vague “skip” because it requires:

- an explicit reason
- an inspectable decision record
- clear downstream legality for the remaining items

## Recommended Usage

Checklist mode should be used when:

- a task has multiple ordered steps
- each step needs its own completion predicate
- the orchestrator should regain control after each step
- the task mixes inspection, planning, implementation, verification, or documentation steps that should remain separately inspectable

Checklist mode should not be used when:

- the task is a single bounded action
- the work is still open-ended exploration without stable structure
- child decomposition is the real required behavior

## Main Contracts In This Bundle

Checklist mode in this workflow-overhaul bundle is described across:

- `2026-03-12_checklist_execution_mode_schema_draft.md`
- `2026-03-12_checklist_item_prompt_contract.md`
- `checklist_examples/example_e2e_route_checklist_instance.yaml`

This overview exists to tie those artifacts back to implementation slices and runtime flows.
