# Phase F13: Idle Detection And Nudge Behavior

## Goal

Detect idle sessions and nudge or escalate safely.

## Rationale

- Rationale: Long-running AI sessions will stall in practice, but the system cannot mistake quiet work for abandonment or corrupt state when nudging.
- Reason for existence: This phase exists to turn idle handling into bounded, policy-driven behavior instead of manual operator guesswork.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 defines the commands and stage semantics idle nudges must restate.
- `plan/features/16_F12_session_binding_and_resume.md`: F12 defines which session is authoritative for idle checks.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides the live session backend used for polling.
- `plan/features/40_F13_idle_screen_polling_and_classifier.md`: F13-S1 is the concrete classifier and polling slice.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/tuning/runtime_tuning_matrix.md`

## Scope

- Database: nudge events and idle-related audit state.
- CLI: nudge and pause-state visibility.
- Daemon: tmux-backed idle detection, alt-screen/screen-state polling policy, bounded nudging, and escalation.
- YAML: heartbeat and idle policy declarations only.
- Prompts: idle-nudge and repeated missed-step guidance prompts.
- Tests: exhaustive threshold, false-positive, escalation, and idle-recovery coverage.
- Performance: benchmark heartbeat monitoring and polling overhead.
- Notes: update idle/tmux notes when concrete polling behavior is frozen.
