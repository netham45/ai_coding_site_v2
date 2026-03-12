# Task: Tmux Codex Trusted Workspace Config Preseed

## Goal

Preseed a session-owned Codex `config.toml` so tmux-backed primary Codex launches start with the intended workspace already trusted instead of waiting on a workspace-trust dialog.

## Rationale

- Rationale: The installed `codex-cli 0.114.0` still shows the workspace-trust prompt during detached tmux launches even with `--yolo` and `--dangerously-bypass-approvals-and-sandbox`, and there is no trust-related feature flag exposed by `codex features list`.
- Reason for existence: This task exists to move trust suppression to a provider-native config surface before falling back to runtime prompt handling, because the user explicitly prefers a launch-time solution over a daemon-side prompt handler.

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
- `plan/tasks/2026-03-12_tmux_workspace_trust_prompt_runtime_acceptance.md`
- `notes/logs/features/2026-03-12_tmux_workspace_trust_prompt_runtime_acceptance.md`

## Scope

- Database: no schema change expected; durable session metadata may record the session-owned Codex config path if that improves auditability.
- CLI: no command-surface change expected.
- Daemon: derive a session-owned Codex home/config path, write trusted-project entries for the intended launch workspace and any required adjacent path Codex resolves during startup, and launch fresh/recovery Codex sessions with that config in effect.
- Website UI: not affected.
- YAML: not affected.
- Prompts: not affected directly.
- Tests: add bounded proof for the generated trusted-workspace config and rerun the real tmux E2E slices that currently stop at the provider trust screen.
- Performance: config generation must remain constant-time and not add repeated steady-state work during polling.
- Notes: update tmux lifecycle and verification checklist notes so provider-side trust preapproval is documented accurately.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_codex_session_bootstrap.py tests/unit/test_session_records.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- fresh and recovery tmux Codex launches write a session-owned Codex config before `os.execvp("codex", ...)`
- the generated config pre-approves the exact workspace paths Codex evaluates during tmux startup
- the real tmux primary session no longer stalls at the workspace-trust dialog for the covered launch path
- notes, checklist, and development-log surfaces describe the provider-side trust preseed behavior honestly
