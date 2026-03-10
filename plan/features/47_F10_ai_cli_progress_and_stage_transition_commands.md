# Phase F10-S4: AI CLI Progress And Stage Transition Commands

## Goal

Implement the AI-facing CLI command family for stage progress and transition control.

## Rationale

- Rationale: Once a session can read its work, it also needs explicit command paths for starting, heartbeating, completing, failing, and advancing stages.
- Reason for existence: This phase exists to make stage mutations durable, validated operations rather than side effects outside the command contract.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 is the parent feature for this command family.
- `plan/features/13_F09_node_run_orchestration.md`: F09 validates and applies the progress and transition mutations.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 shapes pause/resume transitions available through these commands.
- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`: F25 shapes failure and escalation flows triggered by these commands.
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`: F10-S3 provides the read-side commands sessions use alongside these mutations.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/persistence/pause_workflow_event_persistence.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`

## Scope

- Database: ensure progress mutations and stage transitions are durable and ordered correctly.
- CLI: implement:
  - `subtask start`
  - `subtask heartbeat`
  - `subtask complete`
  - `subtask fail`
  - `summary register`
  - `workflow advance`
  - `workflow pause`
  - `workflow resume`
- Daemon: validate transition legality and accept or reject completion authoritatively.
- YAML: transition behavior remains code-owned; YAML only supplies stage contracts and policy.
- Prompts: correction/missed-step prompts must align with the real progress commands.
- Tests: exhaustively cover valid completion, rejected completion, bad transitions, duplicate calls, and pause/fail behavior.
- Performance: benchmark high-frequency progress-command paths.
- Notes: update CLI/runtime docs if transition semantics tighten during implementation.
