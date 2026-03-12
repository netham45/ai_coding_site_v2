# Task: Failed Run Session Inspection Alignment

## Goal

Preserve clear operator and AI inspection of the latest failed run/session after tmux-loss supervision failure, instead of dropping immediately to generic "active run not found" errors.

## Rationale

- Rationale: In the live review, supervision marked the tracked session `LOST`, recovery failed with `restart_launch_failed`, and the run became `FAILED`, but ordinary CLI reads such as `session show --node`, `session recover --node`, `subtask current --node`, and `node run show --node` collapsed into active-run errors while `node show --node` and `node audit --node` still held the real failure evidence.
- Reason for existence: This task exists to make failure and recovery state inspectable through the intended CLI surface after a supervision-caused terminal failure, without forcing operators to infer the cause only from audit history.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/logs/reviews/2026-03-11_tmux_session_supervision_restart_and_failure_plan.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`

## Scope

- Database: reuse existing durable run/session/session-event/workflow-event rows; add or expose any missing failure metadata needed for post-failure inspection.
- CLI: define how `node run show`, `session show --node`, `session events`, and related recovery-status reads should behave when the most recent run failed due to supervision/recovery failure and no active run remains.
- Daemon: add a clear latest-failed-run/session inspection path or graceful fallback for existing active-run commands where the recent failure cause is known and durable.
- Website UI: not directly changed in this slice, but daemon payloads should remain sufficient for future failure-detail views.
- YAML: not affected.
- Prompts: recovery or bootstrap prompts may need wording updates so they do not teach further active-run probing after the daemon has already durably failed the run.
- Tests: add bounded and integration coverage for post-failure inspection and for supervision-caused failure visibility.
- Performance: keep fallback inspection queries targeted to the latest authoritative version/run, not broad historical scans by default.
- Notes: update CLI and tmux lifecycle docs so post-failure inspection behavior is explicit.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py tests/unit/test_daemon_orchestration.py tests/unit/test_run_orchestration.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- after a supervision-caused terminal run failure, operators can inspect the latest failed run and session without relying only on `node audit`
- CLI responses distinguish "no active run exists because the latest run failed" from "node has never had an active run"
- durable failure reason and recovery-attempt evidence are visible through the intended session/run inspection surfaces
- notes and checklist surfaces describe the post-failure inspection behavior honestly
- bounded and real-runtime proof cover the failure-inspection path
