# Feature 13: Generated Task CLI And Operator Inspection

## Goal

Expose template provenance and generated-task lineage through CLI and operator inspection surfaces without inventing a second operator model.

## Main Work

- render authored versus generated decomposition clearly
- expose template ids and step lineage
- keep blocker and state inspection task-oriented

## Implementation Subtasks

- add read models for template provenance and generated-child lineage
- show which child tasks were generated from which template steps
- expose authored versus template-driven decomposition in CLI inspection
- keep blocker and status inspection grounded in ordinary task state

## Main Dependencies

- Setup 02
- Feature 10
- Feature 12

## Flows Touched

- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- there is no inspection vocabulary for generated-task provenance
- the current checklist drafts imply a separate checklist-state inspection surface instead of task lineage inspection
