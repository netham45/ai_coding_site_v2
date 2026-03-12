# Feature 04: Compiled Profile Context And Brief Generation

## Goal

Freeze selected profile state, effective layout, obligations, and generated brief content into compiled workflow state.

## Main Work

- add profile-aware compile context
- generate and persist `workflow brief`
- freeze required roles, updates, verification, and blocked-step metadata

## Implementation Subtasks

- extend compile context to freeze selected profile descriptor, effective layout, and ancestry/profile chain data
- freeze required child roles, required updates, verification obligations, and blocked-action metadata into compiled state
- generate the compiler-owned `workflow brief` from tier prompt, profile prompt, layout context, and discovery guidance
- expose compile failures clearly when profile applicability, layout compatibility, or role coverage checks fail

## Main Dependencies

- Setup 01
- Setup 02
- Feature 01
- Feature 02
- Feature 03

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/db/models.py`
- `src/aicoding/daemon/run_orchestration.py`
- `tests/unit/test_workflows.py`
- `tests/integration/test_workflow_compile_flow.py`

## Current Gaps

- compile is still driven by node-kind `available_tasks` and the first authored base subtask, not by workflow profiles or compiled subtask templates
- there is no compiler-owned `workflow brief`, selected-profile snapshot, or frozen obligation payload in current compiled state
