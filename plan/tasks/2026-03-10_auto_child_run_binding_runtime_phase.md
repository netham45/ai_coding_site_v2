# Task: Auto Child Run Binding Runtime Phase

## Goal

Add a daemon-owned runtime loop that admits and binds ready child runs automatically after child materialization when policy allows.

## Rationale

- Rationale: `auto_run_children` exists in policy surfaces, but there is no daemon loop that actually starts ready child runs today.
- Reason for existence: Without this phase, even correct child creation would still leave the automated hierarchy stalled behind manual operator start/bind commands.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/planning/implementation/optional_pushed_child_sessions_decisions.md`

## Scope

- Database: preserve durable run/session/event evidence for auto-started child work.
- CLI: no new operator command is required; current inspection surfaces must remain sufficient to observe the result.
- Daemon: add an autonomous loop that finds ready child nodes, admits runs, and binds primary sessions.
- YAML: respect existing `auto_run_children` policy instead of inventing a separate hidden knob.
- Prompts: no new prompt assets are required in this phase.
- Tests: add bounded integration proof that ready children auto-start while blocked siblings do not.
- Performance: keep the background scan narrow and idempotent.
- Notes: document the actual scheduling boundary and observability expectations.

## Plan

### Phase 2A: Scheduling helper

1. Add a daemon helper that inspects current parent child sets and identifies ready children.
2. Admit ready child runs with a durable trigger reason.
3. Bind primary sessions for newly admitted child runs.

Exit criteria:

- a ready child transitions to an admitted/bound runtime path without an operator `node run start` or `session bind`

### Phase 2B: Bounded proof and diagnostics

1. Add integration coverage for ready-vs-blocked sibling behavior.
2. Ensure the resulting run/session evidence is visible through existing inspection surfaces.
3. Update notes and development logs.

Exit criteria:

- bounded tests prove autonomous child start behavior and durable inspectability

## Verification

- `python3 -m pytest tests/integration/test_daemon.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- Ready children auto-start through the daemon.
- Blocked children remain blocked until dependencies clear.
- Durable run/session evidence exists for the autonomous start path.
