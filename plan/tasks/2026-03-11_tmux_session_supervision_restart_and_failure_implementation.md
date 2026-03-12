# Task: Implement Tmux Session Supervision, Restart, And Run Failure

## Goal

Implement daemon-owned supervision for tracked tmux-backed primary sessions so lost sessions are recreated automatically when legal and unfinished runs fail durably when restart cannot succeed.

## Rationale

- Rationale: The repository already has explicit bind and recovery operations, but the daemon does not continuously enforce the invariant that tracked primary tmux sessions for active work remain alive.
- Reason for existence: This task exists to execute the supervision plan with one coherent change set across daemon background loops, recovery/failure state transitions, notes, and bounded plus real E2E proof.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/tasks/2026-03-11_tmux_session_supervision_restart_and_failure_plan.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: reuse durable run/session tables and events; add any missing durable failure and supervision events required to explain automatic restart attempts and terminal failure.
- CLI: preserve the existing command family while ensuring inspection surfaces reflect automatic supervision attempts and unrecoverable failure outcomes.
- Daemon: add the background supervision loop, implement restart eligibility checks, and fail unfinished runs when restart is illegal or launch fails.
- YAML: not applicable.
- Prompts: not expected to change directly, but supervision-triggered replacement must stay aligned with the existing tmux/Codex bootstrap contract.
- Tests: add bounded unit/integration coverage for autonomous replacement and unrecoverable failure, and add real tmux E2E proof for autonomous replacement after killing the live tmux session.
- Performance: keep the new loop on the existing session poll cadence and avoid hot-spin or redundant expensive scans.
- Notes: keep the tmux lifecycle note, checklist, and feature checklist aligned with the implemented supervision behavior and proving status.

## Verification

Bounded/document verification:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_session_records.py tests/unit/test_run_orchestration.py tests/integration/test_daemon.py -q
```

CLI/daemon boundary verification:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py -q
```

Real tmux E2E verification:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q
```

## Exit Criteria

- The daemon runs a background supervision loop for tracked primary sessions.
- Lost tracked primary tmux sessions are recreated automatically only when the node is ready to run or otherwise in progress.
- If restart is illegal or launch fails and the work is still unfinished, the active run is marked `FAILED` durably.
- Session and workflow events explain automatic supervision attempts and failure causes.
- Bounded verification passes.
- The real tmux recovery E2E proves daemon-owned replacement after live tmux loss.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log records implementation progress and results honestly.
