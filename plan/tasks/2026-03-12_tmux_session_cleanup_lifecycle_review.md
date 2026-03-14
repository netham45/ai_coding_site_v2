# Task: Tmux Session Cleanup Lifecycle Review

## Goal

Define when daemon-managed Codex/tmux sessions must remain alive versus be cleaned up, and close the immediate real-E2E leak where harness teardown leaves recorded tmux sessions behind.

## Rationale

- Rationale: The runtime note already defined bind, recovery, and lost-session behavior, but it did not say clearly enough when terminal, replaced, superseded, or test-owned tmux sessions should be killed. Real tmux-backed tests were also leaking sessions because harness teardown stopped the daemon and dropped the test database without centrally cleaning the harness-owned tmux sessions.
- Reason for existence: This task exists to make session cleanup policy explicit and to move real-E2E cleanup ownership into the harness instead of relying on ad hoc per-test `tmux kill-session` loops.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`

## Scope

- Database: use the harness-isolated durable session records as the authoritative list of tmux sessions that belong to a real test harness during teardown.
- CLI: no command-surface change in this slice, but the cleanup doctrine must stay aligned with current session inspection and recovery semantics.
- Daemon: clarify the runtime rule for when sessions remain alive versus when terminal, replaced, or superseded sessions should be cleaned up; do not silently treat preserved panes as live forever.
- YAML: not affected.
- Prompts: not affected directly.
- Tests: add bounded coverage for harness-owned tmux cleanup and stop relying only on ad hoc per-test cleanup loops.
- Performance: keep teardown cleanup targeted to the harness's recorded tmux sessions rather than broad tmux-server destruction.
- Notes: update the authoritative tmux lifecycle note and record the review in a development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_e2e_harness.py tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- the authoritative tmux lifecycle note explicitly states when sessions must remain alive and when they should be cleaned up
- real-E2E harness teardown kills the tmux sessions durably recorded for that harness
- the cleanup change has bounded proof
- the required development log is present and cites this task plan
