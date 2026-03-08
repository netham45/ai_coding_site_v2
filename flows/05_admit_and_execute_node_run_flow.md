# Flow 05: Admit And Execute Node Run

## Purpose

Admit a runnable node, bind a primary AI session, and execute compiled subtasks through the canonical command loop.

## Covers journeys

- run a node through the AI command loop
- perform implementation, research, review, or summary subtasks

## Entry conditions

- a node version exists with a compiled workflow
- the node is admissible to run

## Task flow

1. load or create the active node run
2. verify the node is runnable and dependencies are satisfied
3. create or bind the primary session
4. create tmux-backed session state
5. load current workflow cursor
6. retrieve current compiled subtask payload
7. create subtask attempt record
8. mark subtask start and heartbeat
9. execute subtask work
10. register artifacts, outputs, and summaries
11. validate results needed for subtask acceptance
12. mark subtask complete, pause, or fail
13. advance cursor or transfer to failure/pause flow

## Required subtasks

- `admit_or_load_active_run`
- `validate_run_readiness`
- `bind_primary_session`
- `load_current_cursor`
- `retrieve_current_subtask`
- `create_subtask_attempt`
- `mark_subtask_started`
- `execute_compiled_subtask`
- `persist_outputs_and_summaries`
- `accept_or_reject_subtask_result`
- `advance_cursor_or_pause`

## Required capabilities

- `ai-tool session bind ...`
- `ai-tool subtask current|prompt|context ...`
- `ai-tool subtask start|heartbeat|complete|fail ...`
- `ai-tool summary register ...`
- `ai-tool workflow advance|pause|resume ...`

## Durable outputs

- node run record
- primary session binding
- current cursor state
- subtask attempt history
- output and summary records
- accepted completion or failure transition

## Failure cases that must be supported

- node is not admissible
- required dependency unresolved
- session binding fails
- subtask output fails validation
- agent pauses intentionally
- agent fails or times out mid-subtask

## Completion rule

Every step of live execution is reconstructable from durable run, session, subtask, output, and summary history.
