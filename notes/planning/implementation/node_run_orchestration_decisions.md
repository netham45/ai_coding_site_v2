# Node Run Orchestration Decisions

## Scope

This note records the implementation decisions for `plan/features/13_F09_node_run_orchestration.md`.

## Decisions

- run admission now creates a durable `node_runs` row plus its companion `node_run_state` row instead of relying only on the earlier daemon-authority mirror tables
- the current run cursor is initialized from the first compiled subtask in the authoritative compiled workflow for the node version
- subtask execution attempts are persisted in `subtask_attempts` with explicit `RUNNING`, `COMPLETE`, and `FAILED` states
- `subtask complete` does not implicitly advance the cursor in this slice; explicit `workflow advance --node <id>` remains the canonical transition so operator and AI-facing command flow stays inspectable
- pause and resume now synchronize both lifecycle visibility and durable run state
- the earlier `daemon_node_states` and `daemon_mutation_events` surfaces remain as compatibility mirrors for existing inspection paths; they are no longer the canonical durable run record

## Deferred work

- heartbeat persistence and idle-driven attempt updates
- retry semantics and retry admission rules
- validation, review, and testing gate enforcement before advancement
- richer subtask-attempt payloads such as changed-files capture and command-log capture
- session-binding ownership on durable runs

## Notes impact

- runtime notes now describe the explicit separation between attempt completion and workflow advancement
- CLI notes now reflect the current daemon-backed run and subtask surfaces
- database notes now treat `node_runs`, `node_run_state`, and `subtask_attempts` as the canonical durable run-orchestration core for the current slice
