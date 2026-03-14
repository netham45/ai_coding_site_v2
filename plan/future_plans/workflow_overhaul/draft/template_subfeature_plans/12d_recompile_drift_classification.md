# Template Subfeature Plan 12d: Recompile Drift Classification

## Parent Area

- `12 Generated Task Completion And Drift Rules`

## Parent Slice

- `draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`

## Goal

Classify drift when a referenced template changes after children were already generated.

## Implementation Subtasks

- define drift classes for safe, review-required, and invalid template changes
- define how drift classification uses step lineage and compile snapshots
- define operator-visible consequences of each drift class
