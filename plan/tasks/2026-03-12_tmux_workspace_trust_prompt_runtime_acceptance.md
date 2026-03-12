# Task: Tmux Workspace Trust Prompt Runtime Acceptance

## Goal

Make tmux-backed primary-session inspection and idle/nudge polling continue to accept the Codex workspace-trust prompt if it appears after the initial bind/recovery launch window.

## Rationale

- Rationale: After the runtime-repo bootstrap import-path fix, the real tmux E2E suite no longer crashed on `ModuleNotFoundError`, but `test_tmux_task_session_stays_quiet_until_daemon_nudges_then_reports_completion` still failed because the live Codex pane stopped at `Do you trust the contents of this directory?` instead of reaching the daemon nudge text.
- Reason for existence: This task exists to close the remaining real-runtime tmux/Codex startup gap by making workspace-trust prompt handling part of ongoing tmux-backed runtime inspection, not only a best-effort launch-time hook.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`
- `notes/logs/features/2026-03-12_tmux_remain_on_exit_and_live_process_liveness.md`
- `notes/logs/features/2026-03-12_primary_session_prompt_command_contract.md`

## Scope

- Database: no schema change expected; durable session events should record any runtime acceptance of the workspace-trust prompt during later polling.
- CLI: no command-surface change expected, but `session show` and adjacent inspection commands should reflect the post-acceptance pane state instead of leaving the operator on the provider consent screen.
- Daemon: extend tmux-backed trust-prompt handling beyond bind/recovery so inspection, screen classification, and idle-nudge logic can clear the provider gate when it appears after launch.
- Website UI: not directly affected.
- YAML: not affected.
- Prompts: not directly affected.
- Tests: add bounded proof that runtime screen inspection accepts a late-arriving workspace-trust prompt, then rerun the real tmux E2E suites that currently stall behind the provider prompt.
- Performance: keep additional tmux capture work bounded and reuse current polling surfaces.
- Notes: update the tmux lifecycle note and verification checklist so they describe runtime trust-prompt handling honestly.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- a late-arriving Codex workspace-trust prompt is accepted by tmux-backed runtime inspection without requiring manual tmux input from the test harness
- durable session history records the acceptance event when it occurs during ongoing runtime polling
- the real tmux idle/nudge E2E reaches the daemon nudge pane state instead of stalling at the provider trust prompt
- notes, checklist, and development-log surfaces describe the broadened trust-prompt handling accurately
