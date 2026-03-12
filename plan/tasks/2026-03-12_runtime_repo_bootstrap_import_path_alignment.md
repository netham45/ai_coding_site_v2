# Task: Runtime Repo Bootstrap Import Path Alignment

## Goal

Make the primary-session bootstrap and prompt-retrieval Python module commands runnable from the node runtime repo by preserving the daemon's authoritative orchestrator import path instead of overwriting it with a repo-relative `PYTHONPATH=src`.

## Rationale

- Rationale: After primary-session execution cwd moved into the node runtime repo and tmux `remain-on-exit` began preserving fast bootstrap failures, the real tmux E2E pane output showed `aicoding.daemon.codex_session_bootstrap` dying with `ModuleNotFoundError: No module named 'aicoding'`.
- Reason for existence: This task exists to close the remaining real-runtime bootstrap gap by aligning the AI-facing Python module command builder with the actual environment contract used by the daemon and real tmux sessions.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`
- `notes/logs/features/2026-03-12_primary_session_prompt_command_contract.md`
- `notes/logs/features/2026-03-12_tmux_remain_on_exit_and_live_process_liveness.md`

## Scope

- Database: no schema change expected; durable session events may need updated command text if the canonical bootstrap/prompt command rendering changes.
- CLI: command semantics stay the same, but the taught and executed Python module command contract must remain runnable from both the repo root and a node runtime repo.
- Daemon: replace the current relative `PYTHONPATH=src` override with a command/environment builder that preserves the daemon's authoritative orchestrator import path and only appends repo-local Python paths when explicitly needed.
- Website UI: not directly affected.
- YAML: not affected.
- Prompts: any authored or synthesized prompt text that teaches the exact bootstrap/prompt command must be updated if the displayed environment contract changes.
- Tests: add bounded proof for the shared command builder in repo-root and runtime-repo contexts, integration proof that session-event payloads still expose runnable commands, and rerun the real tmux E2E suites that currently fail on the import error.
- Performance: not materially affected; environment construction should stay deterministic and cheap.
- Notes: update the tmux/bootstrap and command-contract notes/checklist so they describe the orchestrator-import-path rule honestly instead of implying that plain relative `PYTHONPATH=src` is always sufficient.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_codex_session_bootstrap.py tests/unit/test_session_harness.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- the shared Python module command builder no longer breaks `aicoding` imports when the working directory is a node runtime repo
- bootstrap and prompt-retrieval command text recorded in session metadata remains accurate and runnable in the real tmux environment
- real tmux E2E no longer fails with `ModuleNotFoundError: No module named 'aicoding'`
- notes, checklist, and development-log surfaces describe the corrected import-path contract honestly
- bounded, integration, and real tmux proof cover the corrected bootstrap import behavior
