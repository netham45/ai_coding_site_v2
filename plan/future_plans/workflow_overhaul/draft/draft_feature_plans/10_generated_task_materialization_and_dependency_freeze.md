# Feature 10: Generated Task Materialization And Dependency Freeze

## Goal

Materialize normal child tasks from task-sequence templates with durable lineage and frozen dependency structure.

## Main Work

- generate child tasks from templates
- persist step-to-task lineage
- enforce idempotent dependency freezing across compile, startup, and recompile

## Implementation Subtasks

- define when template-driven child generation happens
- persist which generated child maps to which template step
- freeze dependency edges among generated siblings as normal task dependencies
- prevent accidental duplicate child generation during retry or rebuild paths

## Main Dependencies

- Setup 02
- Feature 08
- Feature 09

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`

## Relevant Current Code

- `src/aicoding/db/models.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`

## Current Gaps

- there is no durable materialization record for generated child tasks
- dependency freezing today assumes authored children rather than reusable template-driven generation
