# Task: Tmux Remain-On-Exit And Live Process Liveness

## Goal

Enable tmux `remain-on-exit` by default for daemon-managed primary sessions while separating preserved-pane existence from live command/process health so supervision, recovery, and inspection stay correct.

## Rationale

- Rationale: The live tmux E2E failures showed primary-session bind returning `tmux_session_exists=false` immediately after launch because the pane process exited fast enough for tmux to tear the session down before the daemon could inspect it.
- Reason for existence: This task exists to make failed launch state inspectable without losing the pane while preventing the daemon from mistaking a preserved dead tmux session for a healthy running Codex/runtime process.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/tmux_session_manager_decisions.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`

## Scope

- Database: preserve existing durable session/run/session-event rows, but add any missing durable fields or event payload content needed to distinguish `tmux pane preserved after exit` from `runtime still alive`.
- CLI: change session and recovery inspection surfaces so `tmux_session_exists` means pane/session container presence only, and add explicit live-process or live-command status fields for operator diagnosis.
- Daemon: configure tmux-managed primary sessions with `remain-on-exit`, add pane/process liveness inspection, and update bind/recovery/supervision logic to classify preserved-dead panes correctly instead of treating tmux existence as health.
- Website UI: not directly changed in this slice, but daemon payloads must remain sufficient for future session-health and preserved-failure views.
- YAML: not affected; tmux liveness semantics remain code-owned.
- Prompts: not directly changed unless prompt wording currently implies that tmux session existence alone proves the session is still running.
- Tests: add bounded, integration, and real tmux E2E proof for preserved dead panes, live-process detection, and supervision behavior after process exit with tmux still present.
- Performance: keep liveness checks cheap and scoped to the current pane/session; do not require broad polling beyond existing supervision cadence.
- Notes: update tmux lifecycle, CLI surface, recovery appendix, and checklist docs so the new `remain-on-exit` semantics and health fields are explicit.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_harness.py tests/unit/test_session_records.py tests/unit/test_run_orchestration.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- daemon-managed primary tmux sessions are created with `remain-on-exit` enabled by default
- a preserved tmux pane after process exit remains inspectable without being misclassified as a live healthy session
- bind, supervision, recovery, and idle/nudge logic use explicit live-process or live-command status instead of tmux existence alone
- CLI and daemon responses expose both pane existence and live-process health clearly enough for operators and AI sessions to diagnose failures
- notes, checklist, and development-log surfaces document the new tmux semantics honestly
- bounded and real tmux E2E proof cover both successful live sessions and preserved-dead failure sessions
