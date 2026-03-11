# Task: AI Workflow Composite Stage Outcome Implementation Phase 1

## Goal

Implement the first composite AI-facing stage-outcome command, `subtask succeed`, for ordinary execution stages and wire the initial daemon/CLI contract that replaces the low-level success ritual for that scope.

## Rationale

- Rationale: The composite-command design froze `subtask succeed` as the first ordinary execution success path that should stop teaching `summary register -> subtask complete -> workflow advance -> subtask current -> subtask prompt` as the normal AI ritual.
- Reason for existence: This task exists to land the first runtime slice cleanly before command-subtask reporting, broader prompt migration, or additional lifecycle-stage variants.

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
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: reuse the existing durable summary-history, attempt, and run-routing records without introducing a new persistence family in this phase.
- CLI: add `subtask succeed` under the existing `subtask` group with an AI-facing response surface that exposes routed outcome information.
- Daemon: add an authoritative composite mutation that records the summary artifact, completes the current ordinary execution subtask, advances the workflow, and returns a routed outcome.
- YAML: no schema or workflow-definition mutation is expected in this phase.
- Prompts: limit prompt changes to the ordinary execution prompt family required to teach `subtask succeed` for the in-scope leaf execution stage. Broader prompt-family migration remains governed by the later prompt-migration task.
- Tests: add bounded unit and integration coverage for the new command and update prompt-contract coverage for the leaf execution prompt.
- Performance: reduce ordinary success-path command churn for the leaf execution stage by collapsing three daemon mutations and one follow-up probe into one AI-facing command.
- Observability/auditability: preserve summary history, attempt output, and run-routing inspectability even though the AI-facing command is composite.
- Notes: update runtime, CLI, and prompt notes to document the implemented first slice honestly as partial lifecycle coverage.

## Plan

### Phase 1: Command contract and daemon route

1. Add the daemon request/response shape for `subtask succeed`.
2. Implement a daemon-owned helper that:
   - validates the current ordinary execution stage
   - registers the supplied summary artifact durably
   - completes the current running attempt
   - advances the workflow
   - returns a routed outcome payload without requiring post-success probing
3. Keep review and command-subtask stages out of scope for this helper in Phase 1.

### Phase 2: CLI surface

1. Add `subtask succeed` to the CLI parser.
2. Add the CLI handler for reading the summary file and calling the new daemon endpoint.
3. Keep existing low-level commands intact and documented as retained operator/debug primitives.

### Phase 3: Prompt and bounded proof

1. Update the ordinary leaf execution prompt to teach `subtask succeed` as the happy path for successful implementation stages.
2. Add bounded unit/integration coverage for:
   - ordinary execution success routes through the composite daemon helper
   - summary history is still recorded durably
   - CLI round-trip behavior
   - prompt rendering now teaches `subtask succeed`
3. Do not migrate command-subtask, review, parent, pause, recovery, or corrective prompts in this phase.

### Phase 4: Notes, logs, and status

1. Update the relevant runtime/CLI/prompt notes with the implemented Phase 1 boundary.
2. Record the implementation batch in the development log.
3. Update adjacent task-plan references if the implementation boundary changes during coding.

## Verification

- Unit/bounded tests:
  - `python3 -m pytest tests/unit/test_run_orchestration.py tests/unit/test_prompt_pack.py -k 'subtask_succeed or execution_prompt' -q`
- Integration tests:
  - `python3 -m pytest tests/integration/test_daemon.py tests/integration/test_session_cli_and_daemon.py -k 'subtask_succeed' -q`
- Document-family checks:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A dedicated implementation-phase task plan exists for the first composite command slice.
- The daemon and CLI expose `subtask succeed` for ordinary execution stages.
- `subtask succeed` records durable summary history and returns routed run outcome information.
- The ordinary leaf execution prompt teaches `subtask succeed` instead of the old low-level success ritual for this scope.
- Bounded unit/integration coverage exists for the new command.
- The relevant notes and development log are current.
- The canonical verification commands for this phase pass.
