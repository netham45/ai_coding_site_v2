# Task: Capture Workflow Overhaul Future-Plan Note

## Goal

Capture the proposed self-hosted workflow-overhaul idea in a repository-local working note so it is not lost before implementation begins.

## Rationale

- Rationale: The repository already has authoritative feature plans and notes for the current orchestrator shape, but this new idea is still exploratory and should be recorded without overstating implementation readiness.
- Reason for existence: This task exists to preserve the proposed epic/phase/plan/task overhaul as a concrete future-planning artifact while keeping it clearly separate from the repository's current authoritative implementation plan families.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: the workflow-overhaul idea would eventually change the built-in node/task/layout library shape.
- `plan/features/43_F05_prompt_pack_authoring.md`: the workflow-overhaul idea would eventually require revised layout and execution prompts.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: the overhaul directly concerns epic/phase/plan/task structure and default layout behavior.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: the overhaul would likely need profile-aware runtime-policy and prompt selection changes.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task does not change durable product-state schema.
- CLI: not applicable; this task does not change the CLI contract.
- Daemon: not applicable; this task does not change runtime orchestration behavior.
- YAML: not applicable for implementation; the note discusses future YAML changes but does not modify active YAML assets or schemas.
- Prompts: not applicable for implementation; the note discusses future prompt changes but does not modify prompt assets.
- Tests: run document-schema tests for the new governing task plan and development log entry.
- Performance: negligible; documentation-only capture work.
- Notes: add a non-authoritative future-planning note and document that `plan/future_plans/` is a working-notes area.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/README.md` exists and states that the family is non-authoritative working notes.
- `plan/future_plans/workflow_overhaul/draft/` contains the captured workflow-overhaul idea.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
