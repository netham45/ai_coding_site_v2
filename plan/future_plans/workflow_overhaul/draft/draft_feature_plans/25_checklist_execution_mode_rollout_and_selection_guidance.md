# Feature 25: Checklist Execution-Mode Rollout And Selection Guidance

## Goal

Make the checklist execution-mode overview executable by defining how checklist mode is introduced, selected, and constrained in real runtime use.

## Main Work

- define when checklist mode should be chosen instead of normal execution
- align profile-level support, instance-level activation, and operator understanding
- prevent checklist mode from becoming an undocumented freeform escape hatch

## Implementation Subtasks

- define rollout rules for which profiles may opt into checklist mode and which remain single-step only
- define selection guidance for orchestrator and operator choice, including `when_to_use` and `when_not_to_use`
- define the activation path for attaching a checklist instance to a node without inventing a new semantic task type
- document rollout boundaries, limitations, and non-goals for the first checklist-mode implementation wave

## Main Dependencies

- Setup 00
- Feature 08
- Feature 09

## Flows Touched

- `01_create_top_level_node_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`

## Current Gaps

- the checklist overview note existed, but the executable draft queue had no standalone rollout/selection slice for it
- current planning covers checklist mechanics, but not the operational decision model for when checklist mode should be activated
