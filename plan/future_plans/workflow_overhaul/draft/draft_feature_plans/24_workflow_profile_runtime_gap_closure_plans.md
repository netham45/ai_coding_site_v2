# Feature 24: Workflow-Profile Runtime Gap Closure Plans

## Goal

Turn the workflow-profile support-gap note into an executable closure slice that tracks the highest-risk runtime mismatches between current code and target behavior.

## Main Work

- convert the known runtime mismatches into explicit closure work
- keep the draft queue tied to actual code gaps instead of only target-state notes
- provide one place to sequence the most blocking runtime remediations

## Implementation Subtasks

- inventory the highest-risk runtime mismatches such as node-kind-driven compile, profile-unaware materialization, and missing blocked mutation enforcement
- classify which mismatches are prerequisite blockers for workflow-profile routes and which are later adoption work
- map each major runtime gap to the executable draft slices that are supposed to close it
- record the residual gaps that will remain after the main queue so they are not lost behind broad `support gap closure` wording
- explicitly track the immutable compiled-subtask-chain limitation, the rewind-only review remediation posture, and the absence of deterministic corrective expansion for task/plan/phase verification loops

## Main Dependencies

- Setup 02
- Feature 03
- Feature 04
- Feature 22

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `03_materialize_and_schedule_children_flow`
- `06_inspect_state_and_blockers_flow`
- `09_run_quality_gates_flow`
- `11_finalize_and_merge_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/structural_library.py`

## Current Gaps

- the support-gap note existed, but there was no explicit queue item dedicated to reconciling those runtime mismatches against the execution plan
- current draft sequencing can obscure which runtime gaps are still blockers versus later adoption tasks
- current runtime can rewind to an earlier subtask after review findings, but it cannot append new corrective subtasks onto a live compiled chain or materialize bounded corrective descendants from plan/phase verification findings, so the future draft currently overstates how direct the migration path is
