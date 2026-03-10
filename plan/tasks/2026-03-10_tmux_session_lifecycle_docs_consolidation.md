# Task: Tmux Session Lifecycle Docs Consolidation

## Goal

Create one authoritative tmux session lifecycle spec under `notes/specs/runtime/` and repoint the current live documentation and planning references to section anchors in that main file instead of spreading tmux lifecycle guidance across multiple partial notes.

## Rationale

- Rationale: The current tmux/session lifecycle doctrine is fragmented across the runtime loop spec, the recovery appendix, implementation decision notes, and feature plans, which makes the intended tmux lifecycle hard to learn and easy to let drift.
- Reason for existence: This task exists to establish one primary tmux lifecycle document and make current authoritative references point to that single source of truth.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/67_F12_provider_specific_session_recovery_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#backend-abstraction-and-test-posture`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`

## Scope

- Database: document the durable session and event records the tmux lifecycle depends on.
- CLI: document the bootstrap, inspection, attach, resume, and recovery command surfaces tied to tmux-backed sessions.
- Daemon: document fresh launch, recovery classification, replacement launch, and tmux ownership rules.
- YAML: document the boundary that YAML selects prompts/stages while code owns tmux lifecycle control.
- Prompts: document the prompt retrieval, prompt-log, and Codex bootstrap contract for primary sessions.
- Tests: update current live note and plan references so tmux lifecycle expectations map to one authoritative spec.
- Performance: document tmux creation, polling, and recovery as operational concerns without inventing new budgets in this task.
- Notes: add the main spec, reconcile the runtime/recovery notes, and repoint live references to the new section anchors.

## Verification

- Document-family checks after the new task plan and log are added: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Follow-up doc sanity checks after reference updates: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py -q`

## Exit Criteria

- A new tmux lifecycle spec exists under `notes/specs/runtime/`.
- The spec covers fresh bind, prompt/bootstrap, steady-state tmux ownership, recovery classification, replacement/resume, durable records, and inspection surfaces.
- Current live authoritative references to tmux lifecycle guidance point to section anchors in the new spec rather than relying on the old fragmented notes alone.
- A development log records the consolidation work and verification commands run.
