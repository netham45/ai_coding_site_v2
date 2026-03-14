# Templated Task Generation Feature Breakdown

## Purpose

Break templated task generation into concrete implementation features instead of treating it as an informal replacement idea.

This future-plan note replaces the checklist execution-mode feature bundle.

## Feature Slices

### Slice A: Task-Sequence Template Family

Primary goal:

- adopt reusable task-sequence templates as validated authoring assets

Main capabilities:

- `task_sequence_schema_definition`
- `task_sequence_template`
- template step dependency validation
- template applicability rules

### Slice B: Plan And Profile Template References

Primary goal:

- allow plans and applicable workflow profiles to reference a reusable task-sequence template

Main capabilities:

- template references in authored plans or profile defaults
- instance-time selection rules where appropriate
- compile-frozen template metadata

### Slice C: Generated Task Materialization

Primary goal:

- materialize normal child tasks from a template with frozen dependencies and lineage

Main capabilities:

- compile or startup generation
- durable step-to-task lineage
- idempotent re-materialization safeguards

### Slice D: Prompt And Objective Propagation

Primary goal:

- push template step objectives and proving targets into normal generated task prompts

Main capabilities:

- template context injection
- prompt contract alignment
- generated-task objective visibility

### Slice E: Completion, Blocking, And Recompile Rules

Primary goal:

- define how generated tasks behave under normal dependency, blocker, retry, and recompile semantics

Main capabilities:

- standard blocker handling
- dependency readiness based on generated siblings
- recompile drift rules

### Slice F: Operator Inspection Surfaces

Primary goal:

- expose template provenance and generated-task lineage without inventing a second operator model

Main capabilities:

- show which tasks were generated from which template
- inspect template step ids, objectives, and dependencies
- compare authored versus generated decomposition

### Slice G: Website UI Support

Primary goal:

- render generated-task lineage and template provenance through existing workflow views

Main capabilities:

- template badges or provenance detail
- generated-child grouping
- template-aware dependency rendering

### Slice H: E2E Coverage And Flow Adoption

Primary goal:

- prove template-driven materialization through real runtime narratives

Main capabilities:

- startup or compile-time generation from a template
- normal dependency execution across generated children
- operator inspection of generated lineage
- template recompile or migration narratives where applicable

## Suggested Implementation Order

1. Slice A: task-sequence template family
2. Slice B: plan and profile template references
3. Slice C: generated task materialization
4. Slice E: completion, blocking, and recompile rules
5. Slice D: prompt and objective propagation
6. Slice F: operator inspection surfaces
7. Slice H: E2E coverage and flow adoption
8. Slice G: website UI support
