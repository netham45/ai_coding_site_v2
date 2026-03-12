# Task: Workflow Overhaul Prompt Contract And Prompt Rewrite

## Goal

Define an explicit prompt contract for the workflow-overhaul prompt bundle and rewrite every planning-stage prompt in that directory to conform to the contract.

## Rationale

- Rationale: The current workflow-overhaul prompt drafts encode useful role intent, but they do not yet share one explicit contract for lifecycle position, allowed actions, forbidden actions, completion conditions, escalation rules, and structured response expectations.
- Reason for existence: This task exists to prevent prompt drift inside the workflow-overhaul bundle and to make later runtime prompt adoption depend on one reviewed contract rather than many loosely similar prompt styles.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: not directly affected.
- CLI: clarify prompt expectations around operator-visible blocked reasons and structured responses.
- Daemon: clarify what programmatic inputs the future runtime must inject into prompts and what prompt outputs later runtime slices should expect.
- YAML: align prompt assumptions with profile/layout-driven child-role and lifecycle metadata.
- Prompts: add a prompt-contract note and rewrite every planning-stage prompt in `plan/future_plans/workflow_overhaul/prompts/` to follow it.
- Tests: run the document-schema and task-plan verification surface after adding the task/log artifacts and prompt-contract note.
- Performance: keep the prompt contract compact enough to be reusable across tiers without bloating future compiled prompt stacks unnecessarily.
- Notes: update the workflow-overhaul prompt bundle and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a dedicated workflow-overhaul prompt-contract note exists
- every markdown prompt under `plan/future_plans/workflow_overhaul/prompts/` conforms to the shared contract shape
- the prompt README points to the contract note and explains the shared sections
- the required development log records the reviewed files, commands run, and results
