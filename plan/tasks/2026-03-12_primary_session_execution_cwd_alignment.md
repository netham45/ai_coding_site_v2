# Task: Primary Session Execution CWD Alignment

## Goal

Align primary tmux/Codex session working-directory selection with the node's real runtime repo so execution starts in the node version workspace instead of falling back to the repository root.

## Rationale

- Rationale: The live review for node `27e04dd3-55c2-403f-85de-b24935736f44` showed a durable primary-session bind event with `cwd=/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2` while the node's live git repo exists under `./.runtime/git/node_versions/<node_version_id>`.
- Reason for existence: This task exists to close the current gap between the tmux lifecycle doctrine and the runtime implementation by making primary-session execution cwd resolve to the node runtime repo whenever one exists.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`
- `notes/planning/implementation/tmux_session_manager_decisions.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`

## Scope

- Database: keep durable session rows/events authoritative, but ensure they record the node-runtime execution cwd rather than the repo root when a live node repo exists.
- CLI: keep existing session inspection commands, but make their returned `cwd` and attach metadata reflect the corrected execution location.
- Daemon: replace `workspace_root-or-Path.cwd()` primary-session cwd selection with one daemon-owned resolver that prefers the node version's live git repo and falls back only when a node repo does not yet exist.
- Website UI: not directly changed in this slice, but resulting daemon session metadata must stay consistent with website session inspection views.
- YAML: not affected; cwd resolution remains code-owned.
- Prompts: prompt-log and bootstrap context paths derived from the session working directory must remain coherent after the cwd change.
- Tests: add bounded and real-runtime proof that fresh bind and recovery replacement launch in the node runtime repo.
- Performance: keep cwd resolution cheap and deterministic; it should resolve from durable node version identity plus existing repo-path rules, not from broad filesystem scans.
- Notes: update tmux lifecycle and real-E2E workspace-root notes so they explicitly distinguish workspace root from node execution cwd.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_session_records.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- fresh primary-session bind uses the node version's live runtime repo as the execution cwd whenever that repo exists
- provider-agnostic replacement-session recovery uses the same execution-cwd resolver
- durable session events and CLI session inspection surfaces show the corrected cwd
- prompt-log placement remains deterministic and documented after the cwd change
- notes and checklist surfaces explicitly describe the execution-cwd rule
- bounded and real tmux proof cover the corrected cwd behavior
