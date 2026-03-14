# Checklist Execution Mode Feature Breakdown

## Status

Superseded by:

- `2026-03-12_templated_task_generation_feature_breakdown.md`

The active workflow-overhaul direction now centers reusable task-sequence templates that generate normal child tasks.

## Purpose

Break checklist execution mode into concrete implementation features rather than leaving it as one abstract future idea.

This is a future-plan breakdown note.

It is not an implementation plan yet.

## Feature Slices

### Slice A: Checklist Schema Family

Primary goal:

- adopt checklist schema and template families as real validated assets

Main implementation surfaces:

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/resources/yaml/`
- `src/aicoding/structural_library.py`

Main capabilities:

- `checklist_schema_definition`
- `checklist_template_definition`
- `checklist_instance`
- item status vocabulary
- blocker shape
- `not_applicable` shape

Main risk:

- letting AI-authored structure bypass validation

### Slice B: Task/Profile Execution-Mode Support

Primary goal:

- allow task-oriented workflow profiles to opt into checklist execution mode

Main implementation surfaces:

- workflow-profile schema and compiler inputs
- startup/creation request models if instance-time selection is allowed
- compiled workflow context

Main capabilities:

- `execution_mode: checklist`
- profile-level checklist support
- instance-level checklist attachment
- compile-frozen checklist contract visibility

Main risk:

- accidentally turning checklist into a semantic type instead of an execution contract

### Slice C: Durable Checklist Persistence

Primary goal:

- persist checklist instances, item states, blockers, and results durably

Main implementation surfaces:

- database schema
- daemon persistence helpers
- operator inspection reads

Main capabilities:

- active item tracking
- item result history
- blocker persistence
- unblock reevaluation inputs
- `not_applicable` decision persistence

Main risk:

- checklist truth drifting into prompt text rather than durable state

### Slice D: Orchestrator Loop Support

Primary goal:

- let the orchestrator run one checklist item at a time and regain control after each item

Main implementation surfaces:

- daemon execution loop
- run orchestration
- state-transition legality

Main capabilities:

- activate next legal item
- prevent worker-driven self-advancement across multiple items
- return-to-orchestrator after each item result
- dependency-aware selection of the next item

Main risk:

- allowing checklist mode to bypass the normal workflow authority model

### Slice E: Checklist Item Prompt Delivery

Primary goal:

- render and deliver the active-item prompt with the checklist-specific contract

Main implementation surfaces:

- prompt assets
- prompt rendering
- AI-facing work retrieval surfaces

Main capabilities:

- active-item prompt assembly
- `When To Use This` / `When Not To Use This`
- item-specific allowed options
- terminal item return contract

Main risk:

- prompt drift from daemon-enforced item legality

### Slice F: Item Completion And Blocker Enforcement

Primary goal:

- ensure item results are validated against structured completion and blocker rules

Main implementation surfaces:

- daemon mutation validation
- subtask/result registration
- blocked-state inspection surfaces

Main capabilities:

- `completed` validation
- `blocked` validation
- `not_applicable` validation
- structured unblock conditions

Main risk:

- trusting unstructured model claims about completion or blockage

### Slice G: CLI And Operator Inspection Surfaces

Primary goal:

- expose checklist state, blockers, active item, and result history to operators and sessions

Main implementation surfaces:

- CLI parser and handlers
- daemon routes
- read models

Main capabilities:

- show active checklist item
- list item statuses
- inspect blockers and unblock conditions
- inspect prior item results

Main risk:

- checklist runtime existing without adequate inspectability

### Slice H: Website UI Support

Primary goal:

- render checklist state and bounded item actions in the web UI

Main implementation surfaces:

- website operator views
- daemon-backed state reads
- bounded action controls

Main capabilities:

- item list and statuses
- active item detail
- blocker detail
- `not_applicable` reason display

Main risk:

- browser state diverging from daemon-owned authority

### Slice I: E2E Coverage For Checklist Mode

Primary goal:

- prove checklist mode through real runtime narratives

Main implementation surfaces:

- CLI/daemon runtime
- prompt delivery
- persistence
- operator inspection
- website UI where applicable

Main capabilities:

- one-item-at-a-time execution
- blocked item persistence and later unblock
- `not_applicable` handling
- recovery after interruption

Main risk:

- stopping at schema or prompt existence instead of proving runtime behavior

## Suggested Implementation Order

1. Slice A: checklist schema family
2. Slice B: execution-mode support
3. Slice C: durable persistence
4. Slice D: orchestrator loop support
5. Slice F: completion and blocker enforcement
6. Slice E: prompt delivery
7. Slice G: CLI and operator inspection
8. Slice I: E2E coverage
9. Slice H: website UI support
