# Task: Full AI Prompt Command Surface Review

## Goal

Run a comprehensive review of the entire AI-facing command surface across all authored prompts and adjacent prompt-synthesis paths, not just the issues exposed by one transcript.

## Rationale

- Rationale: The prior review/discovery task established important command-surface problems from the real full-tree `cat` transcript, but that transcript only exposed one slice of the prompt library and runtime command loop.
- Reason for existence: This task exists to audit the full prompt-driven AI command surface so the repository can identify every weird or inconsistent command system being taught to AI sessions before any fix work begins.
- This is still a review task, not an implementation-fix task.

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
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `AGENTS.md`

## Scope

- Database: review the durable state and history assumptions implicitly required by the commands taught in prompts.
- CLI: inventory every CLI command or command pattern explicitly taught to AI sessions across prompt assets and prompt-synthesis paths.
- Daemon: identify where prompts are teaching commands whose current daemon semantics are surprising, inconsistent, redundant, or overly low-level for AI use.
- YAML: review prompt-referenced task and hook surfaces where YAML/task structure is indirectly creating weird command rituals.
- Prompts: audit the full authored prompt pack plus synthesized command-subtask and workflow-rendered prompt text for command inconsistencies, duplicate rituals, hidden systems, and odd special cases.
- Tests: run document-family verification for the new task plan/log and any authoritative-doc updates; do not start implementation-side runtime fixes in this task.
- Performance: note prompt-driven command chatter, redundant read-before-write rituals, and repeated recovery-style loops that would inflate session cost.
- Observability/auditability: preserve the distinction between AI-facing workflows and operator/debug workflows while identifying where prompts blur them.
- Notes: produce a durable review artifact that enumerates the full AI command surface and the weird subsystems or command rituals it currently contains.

## Plan

### Phase 1: Full prompt and prompt-synthesis inventory

1. Enumerate every authored prompt file in the packaged prompt pack.
2. Enumerate the non-file prompt-synthesis paths that teach AI sessions command usage, including runtime-generated command-subtask prompts and workflow-rendered parent guidance.
3. Build a complete inventory of every CLI command pattern taught to AI sessions.

### Phase 2: Weird-system classification

1. Group the command systems taught by prompts into distinct subsystems such as:
   - ordinary stage completion
   - command-subtask reporting
   - review routing
   - validation/testing evaluation
   - parent layout generation and child materialization
   - idle/nudge/recovery
   - pause/intervention flows
2. Identify where those subsystems use materially different command shapes or ownership assumptions.
3. Identify prompts that teach special-case exceptions or defensive warnings because the system shape is inconsistent.

### Phase 3: Cross-surface inconsistency review

1. Compare the prompt-taught command systems against the documented CLI and runtime specs.
2. Identify:
   - low-level commands overexposed to AI sessions
   - commands that are composite in one subsystem but low-level in another
   - commands that appear redundant
   - commands that seem to exist only to paper over awkward runtime ownership
3. Separate “prompt wording issue” from “real daemon/CLI system-shape issue.”

### Phase 4: Comprehensive review findings

1. Produce a durable review note with the full command-surface findings, not just transcript-derived issues.
2. Clearly call out every weird subsystem or command ritual that needs later design or remediation consideration.
3. Map the biggest findings back to the already-created follow-on design tasks where possible.

## Verification

- Document-family checks after plan/log updates: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A governing task plan exists for the full prompt-surface AI command audit.
- The development log exists and points back to this task plan.
- The review covers authored prompts and non-file prompt-synthesis paths.
- The resulting note identifies the major weird command subsystems and cross-surface inconsistencies.
- The canonical document-family verification command passes.
