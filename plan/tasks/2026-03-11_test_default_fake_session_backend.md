# Task: Default The Test Harness To The Fake Session Backend

## Goal

Make the pytest-driven test environment default to `AICODING_SESSION_BACKEND=fake` while leaving the application/runtime default unchanged.

## Rationale

- Rationale: The repository's shared bounded test layers already mostly rely on the fake session harness, and requiring every such test to restate that default creates noise while the real tmux E2E harness already passes its own explicit backend.
- Reason for existence: This task exists to move the fake-backend default for tests into one shared pytest location so bounded tests stay concise and deterministic without changing the runtime posture outside tests.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: not applicable.
- CLI: not applicable directly, but CLI tests that rely on the shared pytest environment should inherit the fake backend automatically.
- Daemon: bounded in-process daemon tests should inherit the fake backend automatically unless they opt into tmux explicitly.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: add the shared pytest default, preserve explicit tmux overrides for real-E2E harnesses, and run the affected bounded session/daemon tests.
- Performance: negligible.
- Notes: add the governing task plan and development log only; no broader doctrinal note change is needed because this is a test-harness default, not a runtime default.

## Verification

- Bounded session/daemon checks: `python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q`

## Exit Criteria

- The shared pytest environment defaults `AICODING_SESSION_BACKEND` to `fake`.
- Tests can still override the backend explicitly when needed.
- The real E2E harness continues to pass an explicit `tmux` backend rather than relying on ambient test state.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log exists and records the work honestly.
