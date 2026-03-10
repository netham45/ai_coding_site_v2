# Task: Tmux Codex Session E2E Tests

## Goal

Write the real end-to-end tests for tmux/Codex session handling that prove the live runtime can:

- create a tmux session
- launch a Codex session inside tmux
- run a prompt through that live tmux/Codex session
- go idle
- get nudged through the real CLI/daemon path
- go idle again after the nudge
- report completion through the real runtime path
- report failure/error through the real runtime path

## Rationale

- Rationale: The repository already has some tmux-backed tests, but the strongest proof for idle/nudge behavior still lives in fake-adapter tests and the current tmux runtime does not yet have a dedicated E2E family for the exact session flows requested.
- Reason for existence: This task exists to write the specific tmux/Codex E2E tests needed to prove real session behavior instead of relying on unit-level fake tmux coverage or direct outer-process shortcuts as the primary claim.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: verify durable session, event, and run state only through the real runtime surfaces needed to support the E2E assertions.
- CLI: use the real CLI subprocess path for bind, inspect, nudge, completion, and failure flows.
- Daemon: use the real daemon subprocess path for all tmux/Codex E2E narratives.
- YAML: use the real compiled workflow and prompt-selection surfaces already in the product path; do not bypass them with synthetic YAML-only shortcuts.
- Prompts: exercise the real prompt delivery path used by the live tmux/Codex session and the real nudge prompt path.
- Tests: add dedicated tmux/Codex E2E files or extend the existing tmux E2E family only where the narrative remains clear and fully real.
- Performance: keep the tmux wait loops bounded and deterministic enough for targeted reruns.
- Notes: update only the notes and command docs required to honestly describe the new E2E coverage and any remaining gaps.

## Plan

### Phase 1: Write the live tmux/Codex launch E2E

1. Add a real `requires_tmux` E2E that binds a primary session through the real CLI and real daemon path.
2. Assert that the tmux session exists and that pane output or live session metadata shows a Codex launch rather than a shell-only placeholder.
3. Assert that the intended prompt/workload is visibly running through the live tmux session.

Exit criteria:

- one real E2E test proves tmux session creation and live Codex launch
- the strongest assertions are based on real tmux/session surfaces, not fake adapters

### Phase 2: Write the live prompt execution E2E

1. Extend the launch test or add a second E2E that proves the live tmux/Codex session actually runs the prompt.
2. Assert visible prompt-driven output in the tmux pane or another real operator-visible surface.
3. Keep the proof on the live session boundary rather than direct test-side result injection.

Exit criteria:

- one real E2E test proves the prompt is actually being executed inside the live tmux/Codex session

### Phase 3: Write the idle-detection E2E

1. Add a real E2E that waits for the live tmux/Codex session to become idle using the real runtime path.
2. Assert idle classification through the real CLI/daemon-visible session surface.
3. Keep the wait bounded and diagnosable so failures expose the last pane state.

Exit criteria:

- one real E2E test proves the live tmux/Codex session reaches idle

### Phase 4: Write the nudge E2E

1. Add a real E2E that issues `session nudge --node <id>` through the CLI once the live session is idle.
2. Assert that the nudge is durably visible and that the tmux pane changes because of the nudge.
3. Assert that the session is no longer classified idle immediately after the nudge-triggered activity.

Exit criteria:

- one real E2E test proves a real idle session is nudged and visibly reacts

### Phase 5: Write the repeated-idle E2E

1. Extend the same narrative or add a second E2E that waits for the same live session to become idle again after the nudge response finishes.
2. Assert the second idle classification through the real session surface.
3. Keep the proof tied to the same tmux session rather than creating a fresh session for the second idle check.

Exit criteria:

- one real E2E test proves the idle -> nudge -> idle-again flow against the same live tmux/Codex session

### Phase 6: Write the completion E2E

1. Add a real E2E that proves the tmux/Codex session reports completion through the real runtime path.
2. Require the completion signal to originate from inside the live session path rather than the outer test process directly calling completion as the primary narrative.
3. Assert the resulting durable run/session state through the real CLI-visible surface.

Exit criteria:

- one real E2E test proves session-originated completion through the live tmux/Codex path

### Phase 7: Write the failure/error E2E

1. Add a real E2E that proves the tmux/Codex session reports failure or error through the real runtime path.
2. Require the failure signal to originate from inside the live session path rather than the outer test process directly failing the subtask as the primary narrative.
3. Assert the resulting durable failure state and inspectable summary/error surface through the real CLI-visible path.

Exit criteria:

- one real E2E test proves session-originated failure/error through the live tmux/Codex path

### Phase 8: Run the targeted tmux E2E family and restate coverage honestly

1. Run only the targeted tmux/Codex E2E files for this task.
2. Update command docs, checklists, and notes only as needed to reflect what the tests now really cover.
3. Record the passing and failing results honestly in the development log without overstating completion if some flows remain red.

Exit criteria:

- the targeted tmux/Codex E2E files have been run
- the resulting coverage status is documented honestly

## Verification

- Document-family checks after plan creation: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Current tmux/session baseline: `python3 -m pytest -q tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- Future launch/idle/nudge E2E target: `python3 -m pytest -q tests/e2e/test_tmux_codex_idle_nudge_real.py`
- Future completion/failure E2E target: `python3 -m pytest -q tests/e2e/test_tmux_codex_completion_and_failure_real.py`

## Exit Criteria

- The repository has a governing task plan specifically for the tmux/Codex E2E tests requested.
- The phases are limited to writing and proving the requested E2E tests.
- Completion and failure proof are explicitly required to come from the live session path rather than outer-process shortcut commands as the primary narrative.
- The canonical verification commands for the tmux/Codex E2E files are written down before implementation starts.
