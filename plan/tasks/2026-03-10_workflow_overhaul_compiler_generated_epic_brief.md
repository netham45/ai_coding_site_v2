# Task: Workflow Overhaul Compiler-Generated Epic Brief

## Goal

Document the planned compiler-generated epic briefing surface for the workflow-overhaul design, including the requirement that it be derived from the selected phase-layout YAML and frozen into compiled workflow state.

## Rationale

- Rationale: The workflow-overhaul prompt drafts currently define how an epic should decompose work, but they do not yet specify the separate global briefing surface that should explain the selected phases and their rationale back to the epic session.
- Reason for existence: This task exists to capture the "global epic prompt generated from phase YAML" concept as part of the overhaul design before prompt-pack or compiler implementation work starts.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/prompts/epic/generic.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task does not change durable schema, though it documents future compiled-state expectations.
- CLI: not applicable; this task does not change the CLI contract, though it documents future inspection-surface expectations.
- Daemon: not applicable for implementation; this task only documents a future compiler and runtime behavior.
- YAML: document the requirement that the epic brief be generated from the selected phase layout and workflow profile inputs, including compatibility hints between epic modes and phase layouts.
- Prompts: add a planning-stage draft markdown template for the compiler-generated epic brief and update the generic epic prompt draft to consume it.
- Tests: run relevant document-schema tests for the governing task plan and development log after the note and draft prompt updates.
- Performance: note that generated brief construction should be compile-time and frozen rather than rebuilt ad hoc during runtime loops.
- Notes: update the workflow-overhaul note and prompt draft README to include the compiler-generated epic brief concept.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul note explicitly describes the compiler-generated epic brief and its relationship to phase-layout YAML.
- The workflow-overhaul note records the intended compatibility relationship between epic modes and phase layouts.
- The planning prompt-draft area contains a markdown draft for the epic brief.
- The prompt-draft README lists the new artifact.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
