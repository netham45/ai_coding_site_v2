# Task: Workflow Overhaul Plan And Task Prompt Drafts

## Goal

Author draft markdown prompt files for the workflow-overhaul planning direction covering the `plan` tier and the `task` tier so the full four-tier prompt stack can be reviewed before any runtime prompt-pack changes begin.

## Rationale

- Rationale: The workflow-overhaul bundle already has draft prompts for epic and phase-like decomposition, but the lower two tiers still exist only as profile names in prose rather than reviewable prompt artifacts.
- Reason for existence: This task exists to complete the planning-stage prompt family for all current node kinds without implying that the active built-in prompt pack or runtime task behavior has already changed.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`: future runtime prompt-pack work should promote reviewed lower-tier drafts rather than inventing them ad hoc.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: the lower-tier drafts should stay compatible with the current ladder freeze and not silently redefine active runtime assets.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: task-tier profile prompts will eventually interact with runtime prompt references and policy-aware selection.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `plan/tasks/2026-03-10_workflow_overhaul_epic_and_sub_epic_prompt_drafts.md`
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
- Prompts: add planning-stage draft prompt files for the `plan` tier and `task` tier under the workflow-overhaul future-plan area.
- Tests: run relevant document-schema tests for the governing task plan and log entry after adding the planning prompt files and note references.
- Performance: negligible; documentation-only prompt drafting.
- Notes: update the workflow-overhaul note and prompt-draft README so the lower-tier prompt family is explicitly part of the design package.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul planning area contains markdown draft prompts for the `plan` tier and the `task` tier.
- The `plan` drafts cover the generic baseline plus the currently proposed `plan.authoring`, `plan.execution`, and `plan.verification` variants.
- The `task` drafts cover the generic baseline plus the currently proposed `task.implementation`, `task.review`, `task.docs`, and `task.e2e` variants.
- The workflow-overhaul note and prompt README reference the expanded four-tier prompt bundle.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
