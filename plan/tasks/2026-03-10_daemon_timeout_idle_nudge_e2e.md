# Task: Daemon Timeout Idle Nudge E2E

## Goal

Implement and prove the real runtime behavior where the daemon, not the outer test process, detects an idle tmux/Codex primary session after a real timeout and injects the idle nudge automatically.

## Rationale

- Rationale: The existing tmux/Codex E2E for the silent-until-nudged flow currently uses a manual `session nudge --node <id>` CLI call, which is not proof of daemon-owned timeout nudging.
- Reason for existence: This task exists to implement the missing daemon-owned timeout-nudge runtime path and replace the current manual-trigger E2E proof with an honest real timeout-driven E2E.
- The existing tmux/Codex E2E for the silent-until-nudged flow currently uses a manual `session nudge --node <id>` CLI call.
- That is not proof of daemon-owned timeout nudging.
- The daemon currently exposes the manual nudge endpoint and idle-policy configuration, but the background polling/nudge loop is still placeholder-only.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/40_F13_idle_screen_polling_and_classifier.md`
- `plan/features/72_F13_expanded_human_intervention_matrix.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/idle_detection_and_nudge_behavior_decisions.md`
- `notes/planning/implementation/idle_screen_polling_and_classifier_decisions.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: write durable `screen_polled`, `nudged`, and pause-escalation events through the daemon-owned timeout path.
- CLI: keep `session nudge --node <id>` as the operator control surface, but stop using it as the causal trigger in the daemon-timeout E2E.
- Daemon: replace placeholder-only idle background behavior with a real background loop that polls active primary sessions and applies the existing nudge policy automatically.
- YAML: keep runtime-policy YAML descriptive unless this slice discovers an implementation/documentation mismatch that must be recorded.
- Prompts: keep the silent-until-nudged workload explicit so the session is expected to wait for the daemon-originated prompt.
- Tests: add bounded proof for the background idle-nudge sweep and revise the real tmux/Codex E2E to wait for a daemon-originated `nudged` event.
- Performance: keep the background sweep interval low enough for targeted E2E reruns without turning the daemon loop into a high-noise event writer or repeated-nudge storm.
- Notes: update idle/nudge notes that currently document background loops as placeholder-only.

## Plan

### Phase 1: Make the current proof boundary honest

1. Remove any claim that the manual-nudge E2E proves daemon-owned timeout nudging.
2. Record the gap in the adjacent development log and keep the existing scenario scoped as manual-trigger coverage only until the runtime changes land.

Exit criteria:

- no document or log overstates manual-nudge proof as daemon-timeout proof

### Phase 2: Implement daemon-owned idle sweep and nudge

1. Add a daemon background loop that periodically inspects active primary sessions.
2. Reuse the existing idle classifier and nudge/escalation policy rather than inventing a separate timeout path.
3. Ensure the loop records durable audit events without requiring an operator CLI call.

Exit criteria:

- the daemon can nudge an idle primary session after timeout without any external `session nudge` command

### Phase 3: Add bounded proof for automatic timeout nudging

1. Add a bounded test using the fake session adapter that proves the background-compatible sweep nudges an idle session automatically.
2. Prove the bounded path records the expected durable event and prompt path.

Exit criteria:

- the auto-nudge helper is defended by bounded tests

### Phase 4: Convert the real tmux/Codex E2E

1. Revise the silent-until-nudged E2E so it never calls `session nudge --node <id>`.
2. Wait for the daemon to emit a real `nudged` event after timeout.
3. Fail if the session completes without a daemon-originated nudge or if only first-sample idle evidence exists.

Exit criteria:

- the real E2E proves `quiet -> real idle timeout -> daemon nudge -> completion`

### Phase 5: Reconcile notes, logs, and checklist surfaces

1. Update the idle/nudge implementation note to describe the background loop accurately.
2. Update the E2E log and related checklist surfaces with honest status and verification commands.

Exit criteria:

- notes and logs match the actual runtime and proving boundary

## Verification

- Document-family checks after plan update: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Bounded runtime proof: `python3 -m pytest tests/unit/test_session_records.py -k auto_nudge -q`
- Real tmux/Codex E2E proof: `timeout 240 python3 -m pytest -q tests/e2e/test_tmux_codex_idle_nudge_real.py -k stays_quiet_until_daemon_nudges_then_reports_completion`
- Document consistency rerun if notes/logs/checklists change: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The daemon autonomously nudges idle tmux/Codex primary sessions after timeout.
- The real silent-until-nudged E2E does not call `session nudge --node <id>`.
- The E2E proves a daemon-originated `nudged` event before session-originated completion.
- Notes, logs, and verification commands reflect the new runtime behavior honestly.
