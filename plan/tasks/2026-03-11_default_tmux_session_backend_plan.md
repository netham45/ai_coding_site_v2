# Task: Make Tmux The Default Session Backend

## Goal

Define the implementation plan required to change the repository's default session backend from `fake` to `tmux` without leaving startup, tests, docs, or operator expectations in a contradictory state.

## Rationale

- Rationale: The current default session backend in `src/aicoding/config.py` is `fake`, which makes the out-of-the-box daemon posture diverge from the intended real operator runtime and leads onboarding docs to describe a development-only fallback as the normal default.
- Reason for existence: This task exists to stage the default flip deliberately across config, daemon behavior, tests, and notes so the repo can treat tmux-backed sessions as the standard runtime posture while still preserving explicit fake-backend coverage where it is actually needed.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/39_F12_tmux_session_manager.md`: the default flip depends on the tmux-backed session manager being treated as the primary runtime path rather than an opt-in path.
- `plan/features/16_F12_session_binding_and_resume.md`: the startup, bind, attach, and recovery operator semantics must remain coherent after the default changes.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: the normal AI-facing startup and progress loop should align with the tmux-backed runtime path.
- `plan/features/15_F11_operator_cli_and_introspection.md`: operator inspection surfaces and error messaging need to reflect the new default and its capability requirements.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: the daemon remains the authority even when tmux becomes the default transport/runtime backend.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`
- `README.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: no schema change is expected, but the plan must preserve durable session records, recovery classification, and auditability when tmux is the default runtime transport.
- CLI: adjust startup-facing guidance and capability/error messaging so tmux is treated as the normal backend and fake is treated as an explicit test/development override.
- Daemon: flip the config default to `tmux`, ensure daemon startup and bind flows fail clearly when tmux is unavailable, and verify that the background/runtime posture remains coherent under the new default.
- YAML: not expected to change directly, but the plan must preserve the current code/YAML boundary where session backend choice remains runtime config rather than YAML policy.
- Prompts: review startup/bootstrap guidance so prompt instructions continue to match the tmux-backed primary-session flow after the default flips.
- Tests: identify every unit/integration test that currently relies on the implicit `fake` default and make those tests opt in to `fake` explicitly; keep real tmux E2E tests on the tmux path and keep capability gating explicit.
- Performance: verify there is no accidental startup or polling regression from making tmux the default in normal local runs; document any expected capability checks or startup overhead.
- Notes: update README, getting-started, runtime notes, and command/checklist references so the repository no longer documents `fake` as the normal default posture.

## Verification

- Plan/document schema checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- A concrete staged plan exists for flipping the default session backend from `fake` to `tmux`.
- The plan explicitly covers config, daemon startup, CLI/operator messaging, test fixture impact, documentation updates, and proving commands.
- The plan records which tests must set `AICODING_SESSION_BACKEND=fake` explicitly after the flip instead of relying on the current implicit default.
- The plan distinguishes bounded proof from tmux-gated real-E2E proof.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log exists, cites this task plan, and records both planning start and completion.

## Proposed Execution Stages

### Stage 1: Impact Inventory

- Inventory all code, tests, and notes that currently assume the default backend is `fake`.
- Separate three categories:
  - code paths that should truly default to tmux
  - bounded tests that should continue using fake explicitly
  - docs/messages that currently blur development fallback with runtime default
- Confirm whether any startup or health surfaces currently hide tmux capability failure too late.

### Stage 2: Config And Startup Flip

- Change `Settings.session_backend` in `src/aicoding/config.py` from `fake` to `tmux`.
- Review daemon startup/session adapter creation so missing tmux yields a clear configuration/runtime error rather than a confusing downstream bind failure.
- Review `admin print-settings`, foundation status, and daemon-boundary surfaces to ensure they report the new default clearly.

### Stage 3: Test Fixture Normalization

- Update unit and integration tests that need the fake harness to set `AICODING_SESSION_BACKEND=fake` explicitly.
- Audit helper fixtures and CLI/daemon tests for any implicit dependence on the current default.
- Preserve real tmux E2E tests as tmux-backed and keep capability markers explicit.
- Re-run the bounded session/daemon test layers to prove fake-backed tests still work as an explicit override rather than as ambient default.

### Stage 4: Operator And Doc Alignment

- Update README and the getting-started walkthrough so tmux is the normal runtime default and fake is documented as an explicit development/test override.
- Update the tmux lifecycle and runtime command notes if any wording currently describes tmux as opt-in rather than default.
- Update verification and execution-policy notes if the recommended local startup posture changes.

### Stage 5: Proving Surface

- Run bounded config/session/daemon/documentation tests after the flip.
- Run at least one real tmux-backed session E2E checkpoint to prove the new default posture works in the intended runtime environment.
- Record any remaining environment-gated caveats explicitly rather than weakening the default back to fake in docs.

## Candidate Verification Commands For Implementation

Use these as the initial proving surface for the later implementation change:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_settings.py tests/unit/test_session_harness.py tests/unit/test_session_manager.py tests/unit/test_cli.py -q
python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q
```

These commands are planning targets for the future implementation pass, not a claim that the default flip is already implemented or verified.
