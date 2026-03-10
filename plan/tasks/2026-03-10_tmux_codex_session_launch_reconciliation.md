# Task: Tmux Codex Session Launch Reconciliation

## Goal

Create the implementation and documentation plan for replacing the current shell-only tmux launch path with a Codex-driven launch path that:

- retrieves the current-stage prompt through the CLI
- writes that prompt to `./prompt_logs/<project_name>/...`
- starts Codex with `codex --yolo "Please read the prompt from <cli command to run the tool to retrieve the prompt for the current stage> and run the prompt"`
- uses `codex --yolo resume --last` when the expected tmux session is dead and the system needs to resume work

## Rationale

- Rationale: The current tmux session manager launches an interactive shell, which means the real runtime never crosses into a live Codex-driven execution boundary even when the E2E harness binds a real tmux session.
- Reason for existence: This task exists to define the exact implementation contract for a real Codex-backed session bootstrap and resume path before code changes begin.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
- `plan/reconcilliation/04_tmux_codex_session_launch_reconciliation.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: define the durable launch, resume, and prompt-log metadata that must be recorded for tmux/Codex sessions and recoveries.
- CLI: define the exact current-stage prompt retrieval command that the tmux bootstrap path must reference verbatim in the Codex instruction, while also writing the same prompt to disk for auditability.
- Daemon: replace shell launch planning with Codex launch planning for fresh sessions and `resume --last` planning for dead-session recovery.
- YAML: keep YAML responsible for prompt selection and compiled stage identity, not tmux launch orchestration.
- Prompts: ensure the exact compiled current-stage prompt is what both the CLI retrieval command returns and the prompt-log file stores.
- Tests: define bounded and real E2E proof for launch-command construction, prompt-log creation, tmux session launch, and dead-session resume behavior.
- Performance: keep bootstrap overhead bounded even though prompt export adds one CLI round-trip and one file write per launch.
- Notes: reconcile runtime/session notes so they describe Codex launch and resume honestly instead of a generic shell.

## Verification

- Document-family checks after plan creation: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Future bounded proof target after implementation starts: `python3 -m pytest tests/unit/test_session_manager.py tests/integration/test_session_cli_and_daemon.py -q`
- Future real E2E target after implementation starts: `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`

## Exit Criteria

- The reconciliation plan exists and names the exact Codex launch and resume contract.
- The plan defines the prompt-log path contract under `./prompt_logs/<project_name>`.
- The affected systems, verification commands, and note updates are all explicit before code changes begin.
- A development log records the plan creation and its next implementation step.
