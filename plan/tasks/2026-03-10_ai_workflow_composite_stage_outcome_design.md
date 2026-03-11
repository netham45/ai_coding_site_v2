# Task: AI Workflow Composite Stage Outcome Design

## Goal

Design the composite AI-facing stage-outcome command surface that will replace the current fragmented ordinary success path of `summary register`, `subtask complete`, `workflow advance`, and follow-up next-stage discovery.

## Rationale

- Rationale: The review/discovery task established that the current AI happy path relies on too many low-level daemon mutations, with `workflow advance` acting as a fragile low-level cursor primitive rather than a good AI-facing stage-success contract.
- Reason for existence: This task exists to turn the discovery recommendations into an explicit design/contract package before runtime implementation starts.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: design the durable records and audit expectations for composite stage-outcome commands without removing existing attempt, summary, or result history surfaces.
- CLI: define the candidate command names, request flags, and response payloads for the composite AI-facing stage-outcome path.
- Daemon: define the authoritative mutation semantics for composite stage success, command-result reporting, terminal or next-stage outcomes, and the boundary between ordinary stage completion versus parent-structural mutations.
- YAML: determine whether any task/subtask metadata is needed to select the correct composite command behavior by lifecycle stage, especially for ordinary execution, command-subtask reporting, review routing, parent decomposition, and quality-gate stages.
- Prompts: define how ordinary prompts should migrate from low-level command rituals to the composite command surface without collapsing corrective, recovery, or operator-only flows into the same contract.
- Tests: add or update authoritative design notes and any required document-family coverage only; do not begin runtime implementation in this task.
- Performance: document how the new command surface should reduce conflict retries, prompt-driven read/write chatter, and repeated next-stage probing across the full lifecycle.
- Observability/auditability: preserve explicit artifact, attempt, summary, and event inspectability even when one AI-facing command bundles multiple internal mutations.
- Notes: produce the design note(s) that freeze the composite command contract and map that contract onto the lifecycle stages identified in the structural review.

## Plan

### Phase 1: Lifecycle-stage selection

1. Map the composite-command design target onto the lifecycle stages from `ai_command_lifecycle_structural_review_note.md`.
2. Explicitly decide which stages are in scope for composite AI-facing commands:
   - ordinary execution
   - command-subtask execution
   - review routing
   - possibly selected quality-gate stages
3. Explicitly decide which stages remain out of scope for this command family:
   - bootstrap
   - recovery
   - pause/intervention
   - operator/debug inspection
   - parent structural mutations unless separately justified

### Phase 2: Command-family design

1. Define the candidate composite commands for in-scope stages.
2. For each candidate command, define:
   - request shape
   - durable side effects
   - next-stage, pause, failure, or completion response shape
3. Define compatibility rules with the existing low-level commands.

### Phase 3: Boundary and ownership review

1. Freeze which low-level commands remain operator/debug primitives.
2. Freeze which current AI-facing low-level rituals are replaced by composite commands.
3. Define how review, command-subtask, and parent-decomposition special cases relate to the new command family.

### Phase 4: Design outputs

1. Produce the composite-command design note.
2. Update adjacent runtime/CLI/prompt notes only as needed to record the design boundary, not implementation.
3. Point the later implementation and prompt-migration plans at the final stage-scoped design.

## Verification

- Document-family checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A dedicated task plan exists for the composite AI-facing stage-outcome design phase.
- The design note defines candidate composite commands and their intended response semantics.
- The design note states which lifecycle stages use the composite command family and which remain outside it.
- The design note distinguishes AI-facing composite commands from retained low-level operator commands.
- The design note states how durable history and auditability are preserved.
- The canonical document-family verification command passes.
