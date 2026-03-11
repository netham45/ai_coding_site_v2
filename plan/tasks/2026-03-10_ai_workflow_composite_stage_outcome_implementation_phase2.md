# Task: AI Workflow Composite Stage Outcome Implementation Phase 2

## Goal

Implement the second composite AI-facing stage-outcome command, `subtask report-command`, for command-subtask execution stages and migrate the synthesized command-subtask prompt contract onto that composite path.

## Rationale

- Rationale: The composite-command design froze `subtask report-command` as the command-stage counterpart to `subtask succeed`, but the runtime still teaches command subtasks to stitch together `subtask complete` or `subtask fail` plus `workflow advance`.
- Reason for existence: This task exists to collapse the command-subtask happy path into one daemon-owned command before broader prompt-family migration and protocol hardening continue.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/implementation/ai_workflow_composite_stage_outcome_design_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: reuse existing explicit `execution_result_json`, attempt history, validation/testing/review side tables, and summary history surfaces.
- CLI: add `subtask report-command` under the `subtask` group with required structured-result input and optional bounded failure-summary input.
- Daemon: add an authoritative composite mutation for command-subtask reporting that records the result JSON, completes or fails the attempt as appropriate, advances when appropriate, and returns a routed outcome.
- YAML: no schema or workflow-definition mutation is expected in this phase.
- Prompts: migrate the synthesized command-subtask prompt path to use `subtask report-command`; broader authored prompt-family migration remains under the later prompt-migration task.
- Tests: add bounded unit and integration coverage for the new command and update synthesized command-prompt coverage.
- Performance: reduce command-subtask command churn by collapsing result reporting plus lifecycle routing into one AI-facing mutation.
- Observability/auditability: preserve explicit result JSON, attempt status, and gate evaluation inspectability.
- Notes: update runtime, CLI, and prompt specs plus the feature log to reflect the Phase 2 boundary honestly.

## Plan

### Phase 1: Command contract and daemon route

1. Add the daemon request/response shape for `subtask report-command`.
2. Implement a daemon-owned helper that:
   - validates the current command-stage identity
   - requires a structured result payload with `exit_code`
   - for validation/testing command stages, completes the attempt and advances so daemon-owned gates decide the routed outcome
   - for ordinary command stages, completes and advances on zero exit code, or fails the attempt on non-zero exit code with a bounded failure summary
   - returns a routed outcome payload

### Phase 2: CLI surface

1. Add `subtask report-command` to the CLI parser.
2. Add the CLI handler for reading the required result JSON file and optional failure summary file.
3. Keep retained low-level commands intact.

### Phase 3: Prompt and bounded proof

1. Update the synthesized command-subtask prompt contract to teach `subtask report-command`.
2. Add bounded unit/integration coverage for:
   - ordinary command success
   - ordinary command non-zero failure
   - validation/testing command routing
   - CLI round-trip behavior
   - synthesized prompt rendering now teaches `subtask report-command`

### Phase 4: Notes, logs, and status

1. Update the relevant runtime/CLI/prompt notes with the implemented Phase 2 boundary.
2. Record the implementation batch in the development log.
3. Update adjacent task-plan references if the implementation boundary changes during coding.

## Verification

- Unit/bounded tests:
  - `python3 -m pytest tests/unit/test_run_orchestration.py tests/unit/test_prompt_pack.py -k 'report_command or synthesized_command_subtask_prompt' -q`
- Integration tests:
  - `python3 -m pytest tests/integration/test_daemon.py tests/integration/test_session_cli_and_daemon.py -k 'report_command' -q`
- Document-family checks:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A dedicated implementation-phase task plan exists for the second composite command slice.
- The daemon and CLI expose `subtask report-command` for command-subtask stages.
- The synthesized command-subtask prompt teaches `subtask report-command` instead of the old low-level completion ritual.
- Bounded unit/integration coverage exists for the new command.
- The relevant notes and development log are current.
- The canonical verification commands for this phase pass.
