# Task: AI Workflow Command Surface Review And Discovery

## Goal

Run a dedicated review and discovery stage for the current AI-facing workflow command surface before any remediation work begins.

This task exists to understand why the runtime is currently relying on too many low-level commands, why AI sessions keep mis-sequencing those commands, which misuse cases the daemon should reject more clearly, and which groups of commands should likely collapse into higher-level daemon-owned operations.

## Rationale

- Rationale: The latest real tmux/Codex E2E now passes end to end, but the session transcript still shows repeated command-order mistakes, tolerated conflicts, and an AI-facing workflow that is more fragmented than it should be.
- Reason for existence: This task creates an explicit pause point for review and discovery so the repository can document the real problems, gather evidence from the passing but messy live flow, and decide the correct product direction before starting implementation.
- This is not a fix task. It is a review/discovery task whose output should constrain later design and implementation work.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/automated_full_tree_cat_runtime_preimplementation_note.md`
- `notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
- `AGENTS.md`

## Scope

- Database: review the durable attempt/run/prompt/summary history needed to explain current command mis-sequencing and define which transitions should remain inspectable after any future command-surface simplification.
- CLI: inventory the current low-level AI-facing commands, document where they are redundant or error-prone, and identify candidate higher-level commands without implementing them yet.
- Daemon: document which misuse cases should become clearer state errors, which should become idempotent convenience paths, and which should be collapsed behind one authoritative mutation.
- YAML: review whether the current compiled workflow/prompt contracts are forcing too many low-level steps onto the AI.
- Prompts: inspect where prompts currently require brittle serialized command rituals and where they should eventually move to fewer higher-level commands.
- Tests: use the current passing but messy real E2E as evidence, but do not start implementation-side runtime tests in this stage beyond document-family verification.
- Performance: document the cost of multi-step command chatter and repeated recoverable conflicts in long-running tmux/Codex sessions.
- Observability/auditability: preserve the distinction between operator/debug commands and future AI-facing convenience commands.
- Notes: produce or update the review/discovery notes and logs needed to begin a later design phase honestly.

## Plan

### Phase 1: Evidence collection

1. Review the latest real tmux/Codex E2E transcript and extract concrete command-order failures, repeated conflicts, and examples of tolerated-but-wrong AI behavior.
2. Cross-reference those findings against the current prompt contracts and daemon state transitions so the problem list is evidence-backed rather than anecdotal.
3. Record which issues are transcript-noise only versus actual workflow-contract problems.

### Phase 2: Surface inventory

1. Inventory the current AI-facing command loop across prompt retrieval, attempt start, summary registration, subtask completion, workflow advance, review submission, testing, and validation.
2. Group commands into:
   - commands that must remain low-level operator/debug tools
   - commands that are currently AI-facing but should probably collapse into one higher-level command
   - commands whose misuse should become harder daemon errors
3. Identify where current prompts are compensating for missing daemon-owned workflow operations.

### Phase 3: Ownership and error-policy review

1. Decide which scenarios should be daemon-rejected immediately rather than merely tolerated and recoverable.
2. Decide which scenarios should become idempotent success responses rather than confusing terminal errors.
3. Document the boundary between:
   - allowed retryable races
   - protocol violations
   - future convenience-command responsibilities

### Phase 4: Design recommendations

1. Produce a recommendation set for a simpler AI-facing command surface, including candidate higher-level commands and their intended semantics.
2. Document tradeoffs for:
   - keeping low-level commands for operators
   - exposing higher-level commands for AI sessions
   - maintaining auditability and durable history
3. Identify the minimal next implementation phases required after discovery is complete.

### Phase 5: Follow-on planning

1. Create one or more follow-on implementation task plans only after the review/discovery outputs are written.
2. Do not begin runtime or prompt fixes in this task.

## Verification

- Document-family checks after plan/log updates: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A governing review/discovery task plan exists for the AI-facing workflow command-surface problem.
- The development log for this review/discovery stage exists and points back to this task plan.
- The review scope clearly states that this task does not begin implementation fixes.
- The plan defines concrete evidence-collection, command-inventory, ownership-review, and recommendation phases.
- The canonical document-family verification command passes.
