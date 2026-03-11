# Task: Implement Tmux As The App Default Session Backend

## Goal

Change the application default session backend from `fake` to `tmux` while preserving `fake` as the shared pytest default for bounded tests.

## Rationale

- Rationale: The real runtime path in this repository is tmux-backed, and the app default should match that intended operator posture rather than a bounded-test fallback.
- Reason for existence: This task exists to execute the previously captured tmux-default plan with the smallest coherent change set across config, tests, and operator docs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/tasks/2026-03-11_default_tmux_session_backend_plan.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `README.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: not applicable.
- CLI: update operator-facing wording that described `fake` as the app default.
- Daemon: flip the config default to `tmux`.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: keep the pytest harness defaulting to `fake`, add/adjust settings coverage for the new app default, and run bounded session/config checks.
- Performance: not applicable.
- Notes: update the getting-started guide so it reflects the new app default and the test-only fake fallback accurately.

## Verification

- Bounded verification: `python3 -m pytest tests/unit/test_settings.py tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q`
- Documentation verification: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py -q`

## Exit Criteria

- `src/aicoding/config.py` defaults `session_backend` to `tmux`.
- The shared pytest harness still defaults tests to `fake`.
- The onboarding docs no longer describe `fake` as the application default.
- Verification commands pass.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log records the implementation honestly.
