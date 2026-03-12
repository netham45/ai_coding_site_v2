# Task: Workflow Overhaul Prompt Composition Model

## Goal

Convert the workflow-overhaul prompt bundle from standalone full-profile drafts to an explicit base-plus-overlay composition model.

## Rationale

- Rationale: The new prompt contract is now consistent across the bundle, which makes it a good point to centralize shared lifecycle and enforcement language in tier base prompts rather than duplicating it across every profile prompt.
- Reason for existence: This task exists to make the workflow-overhaul prompt architecture easier to maintain, easier to review for drift, and closer to the likely runtime composition model for real prompt-pack adoption.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_prompt_contract.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: not directly affected.
- CLI: not directly affected beyond future prompt-composition discoverability.
- Daemon: clarify the future prompt-composition direction the daemon/compiler would likely follow.
- YAML: keep prompt reference posture compatible with base-plus-overlay composition.
- Prompts: add explicit base prompt files per tier and slim profile prompts into overlays.
- Tests: run the document-schema and task-plan verification surface after the note and prompt refactor.
- Performance: reduce duplicated prompt content so future composed prompts stay smaller and easier to maintain.
- Notes: update the workflow-overhaul prompt contract, prompt README, and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul notes explicitly recommend a base-plus-overlay prompt model
- the prompt directory contains tier base prompts and profile overlay prompts
- the prompt README explains the composition model
- the required development log records the reviewed files, commands run, and results
