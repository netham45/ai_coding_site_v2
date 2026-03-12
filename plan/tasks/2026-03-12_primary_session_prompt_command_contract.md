# Task: Primary Session Prompt Command Contract

## Goal

Make the AI-facing prompt retrieval and bootstrap command contract self-consistent and runnable in the real primary-session environment.

## Rationale

- Rationale: The live review showed that the durable session launch metadata instructed Codex to use `/usr/bin/python3 -m aicoding.cli.main subtask prompt --node ...`, while the repo's current authoritative local command docs require `PYTHONPATH=src python3 -m aicoding.cli.main ...`.
- Reason for existence: This task exists to remove the current prompt/bootstrap command mismatch so the command recorded in session events, used by the bootstrap helper, documented in notes, and executed inside tmux all refer to the same runnable contract.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/43_F05_prompt_pack_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_cli_bootstrap_and_work_retrieval_commands_decisions.md`
- `notes/logs/doc_updates/2026-03-12_pythonpath_src_command_docs.md`

## Scope

- Database: keep durable prompt/session event records, but ensure recorded `prompt_cli_command` reflects the actual canonical runnable command form.
- CLI: no functional CLI mutation is required unless the fix path chooses a new helper or flag; existing prompt retrieval semantics remain authoritative.
- Daemon: centralize prompt-command construction so `session_manager`, `codex_session_bootstrap`, and prompt/event surfaces cannot drift.
- Website UI: not directly affected.
- YAML: not affected; command construction remains code-owned.
- Prompts: update any bootstrap/session/recovery prompt assets that still teach a command form different from the real canonical launch contract.
- Tests: add bounded proof that the command builder, bootstrap helper, prompt text, and documented local command surfaces stay aligned.
- Performance: not materially affected.
- Notes: update the authoritative docs that currently define the repo-local command posture and the tmux bootstrap contract.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_prompt_pack.py tests/unit/test_resources.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- one shared code-owned helper builds the prompt retrieval command used by launch metadata and bootstrap execution
- the command form taught to Codex is runnable in the real primary-session environment
- authoritative notes and current command docs describe the same command contract
- prompt assets no longer drift from the actual bootstrap contract
- bounded and real-runtime proof catch future command-surface drift
