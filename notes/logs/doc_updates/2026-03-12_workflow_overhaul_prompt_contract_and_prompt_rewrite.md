# Workflow Overhaul Prompt Contract And Prompt Rewrite

## Entry 1

- Timestamp: 2026-03-12T15:20:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite
- Task title: Workflow overhaul prompt contract and prompt rewrite
- Status: started
- Affected systems: notes, prompts, development logs, document consistency tests
- Summary: Began a workflow-overhaul prompt-normalization pass to define a shared prompt contract and rewrite the planning-stage prompt bundle so every prompt includes explicit lifecycle, allowed-action, forbidden-action, completion, escalation, and response sections.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `notes/specs/prompts/prompt_library_plan.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul/draft/prompts -maxdepth 2 -type f -name '*.md' | sort`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/README.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/*/*.md`
- Result: In progress. The prompt bundle has enough content to normalize now, but it still needs one contract note and a full-file rewrite pass so the per-tier prompts stop diverging in structure.
- Next step: Add the prompt-contract note, rewrite the prompt files, run the targeted document tests, and record the final result.

## Entry 2

- Timestamp: 2026-03-12T15:45:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite
- Task title: Workflow overhaul prompt contract and prompt rewrite
- Status: complete
- Affected systems: notes, prompts, development logs, document consistency tests
- Summary: Added a dedicated workflow-overhaul prompt-contract note and rewrote every planning-stage prompt in `plan/future_plans/workflow_overhaul/prompts/` to follow the same section order: role, objective, lifecycle position, inputs, allowed actions, forbidden actions, expected result, completion conditions, escalation or failure, and response contract. The prompt README now points to the contract note, and the task index now includes this rewrite task.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `notes/specs/prompts/prompt_library_plan.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul/draft/prompts -maxdepth 2 -type f -name '*.md' | sort`
  - `rg -n "^Role$|^Objective$|^Lifecycle Position$|^Inputs$|^Allowed Actions$|^Forbidden Actions$|^Expected Result$|^Completion Conditions$|^Escalation Or Failure$|^Response Contract$" plan/future_plans/workflow_overhaul/draft/prompts -g '*.md'`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Added:
    - `plan/future_plans/workflow_overhaul/2026-03-12_prompt_contract.md`
    - `plan/tasks/2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_prompt_contract_and_prompt_rewrite.md`
  - Updated:
    - `plan/future_plans/workflow_overhaul/prompts/README.md`
    - every prompt under `plan/future_plans/workflow_overhaul/prompts/epic/`
    - every prompt under `plan/future_plans/workflow_overhaul/prompts/sub_epic/`
    - every prompt under `plan/future_plans/workflow_overhaul/prompts/plan/`
    - every prompt under `plan/future_plans/workflow_overhaul/prompts/task/`
    - `plan/tasks/README.md`
  - Verification passed: `13 passed in 4.16s`
- Next step: If these planning-stage prompt contracts are accepted, the next implementation-facing move is to mirror the same contract shape in the real prompt-pack assets and bind the named inputs and response contracts to actual compiler and daemon prompt-selection logic.
