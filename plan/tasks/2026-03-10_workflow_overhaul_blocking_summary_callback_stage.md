# Task: Workflow Overhaul Blocking Summary Callback Stage

## Goal

Document the planned workflow stage where AI sessions must provide a human-readable summary through a CLI callback and the workflow remains blocked until that callback is received.

## Rationale

- Rationale: The current system has summary-writing and summary-registration primitives, but the workflow-overhaul planning package does not yet define explicit user-facing summary checkpoints as their own blocking stage contract.
- Reason for existence: This task exists to capture the desired pattern of "ask the AI for a human-readable summary at key points and block until it calls back through the CLI" as part of the overhaul design before runtime implementation begins.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `notes/planning/implementation/prompt_history_and_summary_history_decisions.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: not applicable for implementation; this task only documents a future durable callback and blocking-stage expectation.
- CLI: document the expected callback shape and user-facing summary intent, but do not change the current CLI.
- Daemon: document the future behavior where a workflow stage blocks until the summary callback is received.
- YAML: document the future task or subtask shape for a blocking summary-request stage.
- Prompts: document the future prompt surface that asks the AI for a human-readable status summary meant for user presentation.
- Tests: run relevant document-schema tests for the governing task plan and development log after updating the planning notes.
- Performance: note that the blocking stage should wait on an explicit callback rather than polling ad hoc terminal output.
- Notes: update the workflow-overhaul note with the new blocking-summary-stage concept.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul note explicitly defines the blocking summary callback stage and its purpose.
- The note explains how the stage relates to existing summary-history primitives.
- The note contains at least one draft YAML shape for the proposed stage.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
