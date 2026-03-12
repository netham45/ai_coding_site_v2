# Task: Capture Multi-Provider CLI Session Runtime Future Plan

## Goal

Capture a planning-only future direction for supporting arbitrary CLI coding tools, with Gemini and Claude as the first intended non-Codex targets, while also documenting the need for durable provider session identity instead of relying on Codex `resume --last`.

## Rationale

- Rationale: The current runtime and recovery stack is still effectively Codex-specific even though the durable schema and some recovery surfaces already use provider-oriented names.
- Reason for existence: This task exists to preserve the implementation gap as a concrete future-plan bundle before active coding starts, so later work can begin from repo-aligned notes instead of rediscovering the same constraints from code.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/67_F12_provider_specific_session_recovery_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/provider_specific_session_recovery_surface_decisions.md`

## Scope

- Database: not changing schema in this task, but the future-plan bundle must call out that current `provider_session_id` usage does not yet represent true provider-owned identity for Codex, Gemini, or Claude sessions.
- CLI: not changing commands in this task, but the bundle must outline eventual operator and AI-facing inspection/control surfaces for provider-aware launch, status capture, and resume.
- Daemon: not changing runtime behavior in this task, but the bundle must document the current Codex-only bootstrap path and the need for a provider registry or equivalent abstraction.
- Website UI: not applicable for this planning pass; any future UI work should remain downstream of daemon and CLI contracts.
- YAML: not applicable for this planning pass; provider runtime behavior should remain code-owned unless a narrow declarative policy use case becomes necessary later.
- Prompts: not changing prompt assets in this task, but the bundle must note that bootstrap and recovery prompts likely become provider-specific.
- Tests: run document-family coverage for the new task plan and development log entry.
- Performance: negligible for this documentation-only task.
- Notes: add a non-authoritative future-plan bundle under `plan/future_plans/` and index it without overstating implementation readiness.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- `plan/future_plans/multi_provider_cli_sessions/` exists as a non-authoritative working-note bundle.
- The bundle records the current repo limitation that fresh and recovery launch are Codex-specific today.
- The bundle records the current repo limitation that durable provider identity is not yet distinct from tmux session identity.
- The governing task plan and development log exist and point to the new planning work.
- The documented verification command passes.
