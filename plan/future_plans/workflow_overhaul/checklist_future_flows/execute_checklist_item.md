# Future Flow: Execute Checklist Item

## Purpose

Run one active checklist item and return control to the orchestrator.

## When Used

- a task is in checklist execution mode
- an active item is selected and legally runnable

## Main Runtime Steps

1. inspect checklist instance and active item
2. render the active checklist-item prompt
3. execute only the active item
4. validate the returned terminal item result
5. persist item status, evidence, blockers, or `not_applicable` reason
6. return control to orchestrator

## Invariants

- only one item is active at a time
- worker does not silently advance to the next item
- terminal item results are durable and inspectable
- completion claims do not bypass structured predicates

## Main Surfaces

- daemon execution loop
- CLI or AI-facing work retrieval
- prompt rendering
- checklist persistence

## Main Outcome

One checklist item reaches a terminal item state and the orchestrator regains control.
