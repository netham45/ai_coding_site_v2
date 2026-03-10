# Task: Workflow Overhaul Complete Prompt And YAML Bundle

## Goal

Complete the workflow-overhaul design bundle so the planning-stage prompts, starter workflow-profile YAMLs, and rich layout examples form one coherent four-tier system without broken references or undocumented lower-tier gaps.

## Rationale

- Rationale: The workflow-overhaul bundle already captured the direction clearly, but the prompt and YAML artifacts were incomplete across the lower tiers and still contained broken or ambiguous references.
- Reason for existence: This task exists to make the future-design bundle reviewable as a whole system before any runtime implementation work begins.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`: complete prompt contracts should exist before any authoritative prompt-pack changes are attempted.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: the design bundle should describe a complete profile-aware ladder without silently changing active built-in layouts.
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`: richer layout examples need consistent role/profile contracts before future replacement semantics can be reasoned about.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_helper_assembly_draft.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `plan/future_plans/workflow_overhaul/rich_layout_examples/README.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task does not change durable product-state schema.
- CLI: not applicable; this task does not change the active CLI contract.
- Daemon: not applicable; this task does not change the active runtime implementation.
- YAML: add missing planning-stage starter workflow-profile YAMLs and rich layout example YAMLs, and fix incomplete or broken profile/layout references.
- Prompts: expand the planning-stage prompt family so lower-tier decomposition and execution contracts are explicit and complete.
- Tests: run relevant document-schema tests for the governing task plan and development log after updating the bundle.
- Performance: negligible; documentation-only design work.
- Notes: update the workflow-overhaul notes and README files so the expanded bundle is documented accurately.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul prompt bundle contains complete baseline and profile-specific draft prompts across the four-tier ladder, including lower-tier brief/result contracts where needed.
- The starter workflow-profile bundle covers the currently proposed epic, phase, plan, and task profile families without broken references.
- The rich layout example bundle covers decomposition through `plan -> task` and uses normalized profile-compatibility field names consistently.
- The workflow-overhaul notes and README files describe the completed design bundle accurately.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
