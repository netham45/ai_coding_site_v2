# Flow 06: Inspect State And Blockers

## Purpose

Provide the operator or AI with a reliable explanation of current state, blockers, outputs, and recent decisions.

## Covers journeys

- inspect status
- inspect blockers
- inspect current task/subtask and outputs
- inspect resolved YAML, workflow, and lineage

## Entry conditions

- a node, run, workflow, or session identifier is provided

## Task flow

1. resolve the authoritative node version and active run if any
2. load current lifecycle state, run state, and cursor
3. load dependency and blocker classifications
4. load current or last subtask attempt
5. load recent summaries, failures, and pause reasons
6. load relevant workflow, source YAML, and override lineage
7. load branch, seed, final, or merge state if requested
8. present a normalized explanation to the caller

## Required subtasks

- `resolve_authoritative_target`
- `load_node_and_run_state`
- `load_current_cursor`
- `load_blocker_classification`
- `load_attempt_and_summary_history`
- `load_workflow_and_source_lineage`
- `load_git_and_merge_state`
- `render_read_model`

## Required capabilities

- `ai-tool node show ...`
- `ai-tool node run show ...`
- `ai-tool task current ...`
- `ai-tool subtask current|attempts|logs|output ...`
- `ai-tool node blockers ...`
- `ai-tool node pause-state ...`
- `ai-tool workflow show ...`
- `ai-tool yaml show|resolved|sources ...`

## Durable outputs

- no new business-state mutation is required
- optional access/audit log if desired

## Failure cases that must be supported

- requested node version is superseded and caller did not specify which lineage to inspect
- blocker state is ambiguous because authoritative target cannot be resolved
- current state view conflicts with live runtime data

## Completion rule

The caller can answer:

- what is running
- what last happened
- what it is waiting on
- what the next required action is

without attaching to the session or inspecting the database manually.
