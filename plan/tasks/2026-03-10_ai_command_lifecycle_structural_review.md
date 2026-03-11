# Task: AI Command Lifecycle Structural Review

## Goal

Plan and complete a structural review of the full AI command lifecycle so the repository can produce one coherent lifecycle note that maps all actual AI flows, stage boundaries, command systems, and handoff points.

## Rationale

- Rationale: The broad prompt-surface audit has already shown that the repository has multiple overlapping AI command systems rather than one clean command loop.
- Reason for existence: This task exists to finish that review structurally by turning the prompt/runtime/flow inventory into a staged lifecycle map rather than a loose list of weird systems.
- This is a review-and-planning task, not an implementation-fix task.

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
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `AGENTS.md`

## Scope

- Database: identify the durable checkpoints, histories, and state transitions the lifecycle depends on at each AI stage.
- CLI: map which CLI commands appear in each lifecycle stage and distinguish canonical AI-facing commands from operator/debug reads.
- Daemon: map the daemon-owned transitions, composite commands, and strict low-level mutations that define each stage boundary.
- YAML: identify where YAML task, hook, and policy structure creates distinct lifecycle branches or special cases.
- Prompts: map authored and synthesized prompts into one lifecycle sequence, including bootstrap, execution, quality gates, pause, recovery, idle correction, child work, and parent orchestration.
- Tests: update planning/log notes and run document-family verification only; do not start runtime or prompt fixes in this task.
- Performance: identify high-chatter or high-roundtrip lifecycle stages that should be called out explicitly in the review.
- Observability/auditability: ensure each lifecycle stage identifies the operator inspection surfaces and durable evidence expected for that stage.
- Notes: produce the planning structure needed to finish the lifecycle review and create the eventual authoritative lifecycle note.

## Plan

### Phase 1: AI flow inventory

1. Enumerate every actual AI flow family currently present in code, prompts, and notes.
2. Group them into lifecycle categories such as:
   - top-level startup and binding
   - stage bootstrap and context loading
   - ordinary execution
   - command-subtask execution
   - review/validation/testing/docs
   - parent decomposition and child creation
   - child-session delegation and merge-back
   - pause/intervention
   - idle/missed-step correction
   - recovery/replacement/resume
   - terminal completion
3. Identify which families are primary flows versus corrective or exceptional flows.

### Phase 2: Stage-by-stage lifecycle map

1. For each lifecycle category, document:
   - entry conditions
   - prompts that can drive it
   - CLI/daemon commands taught to the AI
   - durable state or audit records expected
   - handoff or exit conditions
2. Identify where one stage can legally branch into another.
3. Mark which stage boundaries are currently clean versus which are split across multiple overlapping systems.

### Phase 3: Structural inconsistency review

1. Identify where lifecycle stages have multiple competing prompt families or command rituals.
2. Identify where corrective flows duplicate ordinary flows with only wording changes.
3. Identify where lifecycle stages are only partially specified in notes versus being inferred from code or prompts.
4. Separate:
   - lifecycle documentation gap
   - prompt-library boundary problem
   - daemon/CLI ownership problem

### Phase 4: Lifecycle-note planning

1. Define the outline for the future full AI command lifecycle note.
2. Freeze the required sections for that note, including:
   - lifecycle stages
   - command systems
   - durable evidence
   - operator surfaces
   - branch and recovery paths
   - known weird or transitional systems
3. Decide which existing notes should remain source notes versus which should later defer to the lifecycle note.

### Phase 5: Completion artifacts

1. Update the review note and development log with the finished structural lifecycle findings.
2. Create the follow-on task plan for authoring the actual full AI command lifecycle note if that note is not completed within this task.
3. Do not begin runtime or prompt fixes in this task.

## Verification

- Document-family checks after plan/log updates: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A governing task plan exists for completing the AI command review structurally.
- The development log exists and points back to this task plan.
- The remaining review work is explicitly broken into lifecycle phases rather than an open-ended audit.
- The plan defines the path from flow inventory to a stage-by-stage lifecycle map and lifecycle-note outline.
- The canonical document-family verification command passes.
