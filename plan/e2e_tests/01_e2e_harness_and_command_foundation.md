# Phase E2E-01: E2E Harness And Command Foundation

## Goal

Build the reusable real-stack harness and canonical command foundation needed for feature-level E2E coverage.

## Rationale

- Rationale: Feature-level E2E tests cannot be generated consistently unless the repo has one reusable harness for the real daemon, real CLI, real database, and real workspace boundaries.
- Reason for existence: This phase exists to make future E2E authoring additive and repeatable instead of forcing each suite to rediscover how to launch and isolate the real stack.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/39_F12_tmux_session_manager.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: ensure real E2E fixtures can create isolated real PostgreSQL-backed state and verify durable outcomes without cross-test contamination.
- CLI: standardize real CLI subprocess invocation and canonical E2E commands.
- Daemon: standardize real daemon subprocess startup, auth token behavior, health checks, readiness waits, and teardown.
- YAML: ensure the harness can point the runtime at project/builtin YAML roots without monkeypatched shortcuts.
- Prompts: ensure the harness can exercise real prompt assets and prompt history behavior as suites expand.
- Notes: document the canonical E2E commands and environment assumptions.
- Tests: create reusable E2E fixtures/helpers rather than duplicating launch logic in each suite.
- Performance: keep the harness reliable and bounded enough to support repeated feature-family E2E runs.

## Work

- harden `tests/fixtures/e2e.py` and `tests/helpers/e2e.py` into the canonical real-stack harness
- add support for isolated workspace roots as first-class product-owned runtime inputs
- add support for isolated git repos and runtime directories
- add support for optional tmux and provider-backed modes without making them mandatory for all suites
- define canonical E2E command families:
  - core E2E smoke
  - compile/orchestration E2E
  - session/recovery E2E
  - quality/audit E2E
  - git/rebuild/cutover E2E
- document required env vars and skip/gate behavior

## Deliverables

- stable real E2E harness fixtures
- stable real CLI helper interface
- stable daemon startup and readiness helpers
- documented E2E command families and markers

## Exit Criteria

- new E2E suites can reuse one harness instead of inventing their own launch model
- canonical E2E commands are written down and reusable
- the harness no longer depends on hidden assumptions or one-off shell knowledge
