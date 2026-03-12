# Task: Remove Tmux Codex Trust UI Fallback

## Goal

Remove the daemon-side tmux/Codex workspace-trust UI interaction code so provider-side trust preseed is the only supported startup path for daemon-managed primary Codex sessions.

## Rationale

- Rationale: The repository now has a provider-side launch path that seeds a session-owned `CODEX_HOME`, writes trusted-workspace config, copies Codex auth state, and launches Codex with explicit `-C <workspace>`.
- Reason for existence: This task exists to delete the older tmux send-keys trust-handler path so the runtime no longer carries two competing startup mechanisms for the same provider concern.

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
- `plan/tasks/2026-03-12_tmux_codex_trusted_workspace_config_preseed.md`
- `notes/logs/features/2026-03-12_tmux_codex_trusted_workspace_config_preseed.md`
- `notes/logs/features/2026-03-12_tmux_workspace_trust_prompt_runtime_acceptance.md`

## Scope

- Database: no schema change expected, but durable session-event expectations may change because `workspace_trust_prompt_accepted` and related fallback-driven event flows should disappear.
- CLI: no command-surface change expected.
- Daemon: remove the tmux trust-prompt detection/acceptance helpers from `session_records.py`, stop classifying the provider trust screen as a daemon-managed runtime branch, and make launch/recovery rely solely on provider-side trust preseed.
- Website UI: not affected.
- YAML: not affected.
- Prompts: not affected directly.
- Tests: delete or rewrite bounded tests that assert daemon-side trust UI handling; add/update tests so the only supported contract is provider-side trust preseed plus normal tmux/Codex runtime behavior.
- Performance: should improve slightly by removing extra capture/send-keys loops from bind/recovery/runtime inspection.
- Notes: update tmux lifecycle and verification checklist notes so they no longer describe daemon-managed trust UI acceptance as a supported fallback.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py tests/unit/test_session_manager.py tests/unit/test_codex_session_bootstrap.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- the daemon no longer sends tmux input to accept Codex workspace trust prompts
- `session_records.py` no longer carries the trust-prompt constants, helper functions, event writes, or screen-classification branches associated with the old fallback
- notes, checklist, and development logs describe provider-side trust preseed as the only supported startup mechanism for this concern
- bounded tests and the relevant real tmux E2E slices pass without the deleted fallback code
