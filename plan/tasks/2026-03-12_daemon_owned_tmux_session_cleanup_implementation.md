# Task: Daemon-Owned Tmux Session Cleanup Implementation

## Goal

Implement daemon-owned cleanup for tmux/Codex sessions so terminal, replaced, superseded, and completed delegated sessions are killed automatically instead of relying on test harness teardown or ad hoc operator cleanup.

## Rationale

- Rationale: The authoritative tmux lifecycle note now states when a session should remain alive and when it should be removed, but the runtime still lacks a single daemon-owned cleanup path that enforces those rules in production behavior.
- Reason for existence: This task exists to turn the new cleanup doctrine into actual daemon behavior across session replacement, terminal run completion, version supersession/cutover, and delegated child-session completion, while preserving enough evidence for inspection before teardown.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/19_F14_optional_pushed_child_sessions.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`
- `plan/tasks/2026-03-12_tmux_session_cleanup_lifecycle_review.md`
- `notes/logs/reviews/2026-03-12_tmux_session_cleanup_lifecycle_review.md`

## Scope

- Database: reuse durable session/run/version state as the authority for cleanup eligibility; add durable session events if needed so cleanup actions and inspection-retention decisions remain auditable.
- CLI: preserve existing inspection commands while ensuring post-cleanup reads still expose the durable session/run history rather than silently failing because the tmux pane was removed.
- Daemon: add a single cleanup helper used by terminal-run completion, session replacement, supersession/cutover invalidation, and delegated child-session completion or abandonment; support bounded retention for remain-on-exit failure evidence before final kill.
- YAML: not affected directly.
- Prompts: not expected to change directly, but any cleanup after supervision failure must remain aligned with existing recovery/failure prompt expectations.
- Tests: add bounded and integration coverage for cleanup eligibility and timing, plus real tmux E2E proof that replaced/terminal sessions do not leak after the runtime reaches the cleanup point.
- Performance: avoid broad tmux-server scans; cleanup should target only the tmux session names durably associated with the affected run/session transition.
- Notes: keep the tmux lifecycle note, related recovery docs, and verification/checklist surfaces aligned with the implemented cleanup semantics and proving status.

## Verification

Bounded and integration verification:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py tests/unit/test_session_harness.py tests/unit/test_child_sessions.py tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
```

Document verification after note/log/checklist updates:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

Real tmux verification:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q
```

## Exit Criteria

- the daemon owns tmux cleanup for replaced primary sessions, terminal runs, superseded/cut-over stale sessions, and completed or abandoned delegated child sessions
- cleanup decisions are derived from durable session/run/version truth rather than opportunistic tmux discovery alone
- preserved dead panes remain inspectable long enough for bounded failure evidence capture, then are cleaned automatically
- `session show`, `session events`, `node run show`, and related inspection surfaces remain informative after tmux cleanup
- bounded and integration coverage prove cleanup eligibility and no-longer-live semantics
- real tmux E2E proves the runtime reaches cleanup without leaking sessions for the covered narratives
- the required notes, checklist surface, and development logs are updated honestly
