# Task: AI Workflow Prompt Migration And Protocol Hardening

## Goal

Plan the implementation phase that will migrate prompts to the future composite stage-outcome command surface and harden the runtime/E2E expectations around protocol compliance.

## Rationale

- Rationale: Discovery established that the current prompts are compensating for low-level workflow fragmentation and that the passing real E2E proves survivability more than clean protocol obedience.
- Reason for existence: This task exists to govern the later prompt/runtime hardening pass after the composite command design and implementation are ready.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
- `AGENTS.md`

## Scope

- Database: not expected to be the primary change surface, but any new durable protocol-compliance evidence or event recording must be documented if introduced.
- CLI: migrate prompt-facing command instructions to the composite stage-outcome path while preserving low-level operator commands for recovery and debugging.
- Daemon: define the protocol-hardening expectations for misuse cases such as redundant post-review advancement, post-completion probing, and corrective-flow drift between ordinary execution and recovery paths.
- YAML: review whether built-in task/subtask definitions need metadata changes to support the new prompt contract cleanly across lifecycle stages, including parent decomposition and quality-gate stages.
- Prompts: update leaf, command, review, parent, runtime, recovery, pause, quality, testing, and docs prompts according to the lifecycle-stage ownership model rather than only patching the transcript-exposed prompts.
- Tests: plan bounded and real E2E proof that the AI happy path no longer depends on low-level retry choreography.
- Performance: document reduced command churn and fewer conflict retries as an explicit expected outcome.
- Observability/auditability: ensure prompt simplification does not remove operator inspection or replay surfaces.
- Notes: update runtime, CLI, prompt, and lifecycle notes to reflect the post-migration contract honestly.

## Plan

### Phase 1: Prompt-family migration map

1. Group prompt families by lifecycle stage:
   - bootstrap
   - ordinary execution
   - command-subtask execution
   - parent decomposition
   - quality gates
   - pause/intervention
   - idle/missed-step correction
   - recovery and replacement
2. Mark which families should adopt composite commands directly.
3. Mark which families should remain mostly behavioral or operator-guidance prompts.

### Phase 2: Corrective-family consolidation plan

1. Review the overlapping `runtime/*`, `recovery/*`, and `pause/*` families.
2. Define which prompt families should merge, defer, or become more explicitly stage-scoped.
3. Define which current defensive warnings should disappear once runtime ownership is clearer.

### Phase 3: Protocol-hardening targets

1. Freeze the misuse cases that should be rejected or surfaced more clearly after migration.
2. Define bounded and E2E assertions for:
   - no redundant post-review advancement
   - no post-completion probing through low-level commands
   - no ordinary success-path reliance on low-level retry choreography
3. Define which old low-level command paths remain valid only for operators and recovery.

### Phase 4: Migration outputs

1. Produce the migration and protocol-hardening note set.
2. Sequence the later implementation and E2E work by lifecycle stage rather than by individual prompt file.
3. Keep the distinction between AI-facing workflow prompts and operator/debug surfaces explicit.

## Verification

- Document-family checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A dedicated task plan exists for the later prompt-migration and protocol-hardening phase.
- The plan names the affected prompt families and protocol-hardening targets across the full lifecycle, not only the transcript-exposed prompts.
- The plan states the expected bounded and E2E proof layers for the migration.
- The plan preserves the distinction between AI-facing workflow commands and low-level operator/debug commands.
- The canonical document-family verification command passes.
