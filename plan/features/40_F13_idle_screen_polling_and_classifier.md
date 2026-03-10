# Phase F13-S1: Idle Screen Polling And Classifier

## Goal

Implement the concrete idle classifier for active sessions using bounded screen-state polling.

## Rationale

- Rationale: Idle detection needs a concrete classifier and polling strategy, not just a policy concept, because the daemon has to distinguish quiet work from stalled work.
- Reason for existence: This phase exists to freeze the low-level evidence the runtime uses before it issues nudges or escalations.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`: F13 is the parent feature for this low-level classifier slice.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides the backend screen state being polled.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 defines the current stage and next-step guidance nudges must reference.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/tuning/runtime_tuning_matrix.md`
- `notes/planning/implementation/tmux_and_session_harness_decisions.md`

## Scope

- Database: persist idle-detection and nudge-related events with timestamps and classifier reasons.
- CLI: expose enough state for operators to understand why a session was treated as idle.
- Daemon: poll screen/alt-screen state, compare snapshots over time, and classify sessions as active, quiet, or idle.
- YAML: runtime policy may define poll interval, comparison windows, and nudge thresholds.
- Prompts: idle nudgers must restate the current stage and next required CLI actions accurately.
- Tests: exhaustively cover unchanged-screen detection, false-positive resistance, polling gaps, and escalation thresholds.
- Performance: benchmark polling cost and classifier overhead under many concurrent sessions.
- Notes: update idle/nudge notes when the classifier is frozen.
