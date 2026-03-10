# Task: Workflow Overhaul Epic And Sub-Epic Prompt Drafts

## Goal

Author draft markdown prompt files for the workflow-overhaul planning direction covering the epic tier and the sub-epic tier so those prompts can be reviewed and iterated on before any runtime prompt-pack changes begin.

## Rationale

- Rationale: The workflow-overhaul note now defines profile-aware tier contracts, but those contracts still need concrete prompt drafts in file form so the prompt surface can be reviewed as an artifact family instead of only as prose embedded in a note.
- Reason for existence: This task exists to create planning-stage prompt assets for epic and sub-epic work without implying that the active built-in prompt pack has already changed.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`: eventual runtime prompt-pack changes should build from these drafts rather than inventing a separate direction later.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: the prompt drafts should remain compatible with the current ladder freeze and not silently redefine active runtime assets.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: profile-aware prompts will eventually need prompt-reference and policy integration.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task does not change durable product-state schema.
- CLI: not applicable; this task does not change the CLI contract.
- Daemon: not applicable; this task does not change runtime orchestration behavior.
- YAML: not applicable for implementation; this task does not modify active runtime YAML or schema families.
- Prompts: add planning-stage draft prompt files for epic and sub-epic profiles under the workflow-overhaul future-plan area.
- Tests: run relevant document-schema tests for the governing task plan and log entry after adding the planning prompt files and note references.
- Performance: negligible; documentation-only prompt drafting.
- Notes: update the workflow-overhaul note to reference the new draft prompt files and clarify scope.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul planning area contains markdown draft prompts for the epic tier and sub-epic tier.
- The drafts cover the generic baseline plus the currently proposed epic and sub-epic profile variants.
- The workflow-overhaul note references the prompt-draft directory as part of the future design package.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
