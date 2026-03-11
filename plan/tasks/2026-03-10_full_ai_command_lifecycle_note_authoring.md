# Task: Full AI Command Lifecycle Note Authoring

## Goal

Author the first dedicated note that describes the full AI command lifecycle across startup, execution, quality gates, parent/child flows, pause/intervention, idle correction, recovery, and terminal completion.

## Rationale

- Rationale: The structural review now maps the actual lifecycle stages and the overlapping systems that currently define them, but the repository still lacks one authoritative cross-source lifecycle note.
- Reason for existence: This task exists to turn the completed structural review into the actual lifecycle note that future prompt/runtime/CLI cleanup work can reference.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: describe the durable evidence and audit surfaces for each lifecycle stage.
- CLI: describe the command surfaces that appear at each lifecycle stage.
- Daemon: describe the stage-transition ownership model and composite-versus-low-level command boundaries.
- YAML: describe where YAML task and hook structure introduces lifecycle branches.
- Prompts: map authored and synthesized prompts into the lifecycle explicitly.
- Tests: run document-family verification for the lifecycle note and any adjacent authoritative-doc updates.
- Performance: identify the lifecycle stages where command churn, repeated reads, or recovery loops materially affect AI-session cost or operator latency.
- Notes: author the lifecycle note and update adjacent references if needed.

## Verification

- Document-family checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A governing task plan exists for authoring the full AI command lifecycle note.
- The lifecycle note exists and follows the outline from the structural review.
- The lifecycle note clearly distinguishes primary, corrective, and exceptional AI flows.
- The lifecycle note points back to the runtime, tmux, CLI, and prompt specs as source notes.
- The canonical document-family verification command passes.
