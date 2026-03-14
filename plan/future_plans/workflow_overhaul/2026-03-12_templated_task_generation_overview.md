# Templated Task Generation Overview

## Purpose

Capture the replacement direction for the workflow-overhaul planning bundle.

This future-plan note supersedes the earlier checklist-execution-mode framing.

It is not an implementation claim.

## Core Position

There should not be a separate checklist runtime.

The runtime should continue to execute normal workflow tasks.

The planning distinction is:

- one-off decomposition: a plan authors its child tasks directly
- templated decomposition: a plan or profile references a reusable task-sequence template and the system materializes normal child tasks from it

After materialization, the runtime should only see normal tasks, dependencies, prompts, and results.

## Why This Replaces Checklist Mode

The earlier checklist direction was trying to solve a real problem:

- repeated multi-step work was being handled informally
- recurring decompositions were not reusable
- step ordering and proving expectations could drift across similar runs

The checklist framing added too much second-system complexity:

- checklist-specific schema families
- checklist-specific runtime state
- checklist-specific prompt contracts
- checklist-specific operator surfaces
- checklist-specific E2E narratives

If meaningful steps deserve durable state, blockers, retries, proving, and operator visibility, they should usually just be tasks.

## New Runtime Model

Keep two runtime realities only:

1. normal authored tasks
2. normal generated tasks

The runtime should not need a third execution model for checklist items.

## Authoring Model

Use reusable task-sequence templates when:

- the same decomposition recurs across many plans or profiles
- objectives and dependencies should stay consistent
- the system should materialize a standard route instead of relying on ad hoc child authoring

Use one-off authored tasks when:

- the decomposition is unique to one plan
- the exact children are part of the bespoke design work
- reuse would not meaningfully reduce drift or operator ambiguity

## Practical Rule

If a step should be:

- visible independently
- blocked independently
- retried independently
- proven independently
- inspected independently

then it should be a task.

Templates may generate those tasks, but the runtime should still treat them as ordinary tasks.

## Main Contracts In This Bundle

The replacement direction is described across:

- `2026-03-12_task_sequence_template_schema_draft.md`
- `2026-03-12_generated_task_objective_contract.md`
- `2026-03-12_templated_task_generation_feature_breakdown.md`
- `2026-03-12_templated_task_generation_flow_impact.md`
- `task_sequence_examples/example_e2e_route_template.yaml`

## Superseded Direction

The following checklist-specific notes remain only as historical draft context and should not drive new implementation planning:

- `2026-03-12_checklist_execution_mode_overview.md`
- `2026-03-12_checklist_execution_mode_schema_draft.md`
- `2026-03-12_checklist_item_prompt_contract.md`
- `2026-03-12_checklist_execution_mode_feature_breakdown.md`
- `2026-03-12_checklist_execution_mode_flow_impact.md`
