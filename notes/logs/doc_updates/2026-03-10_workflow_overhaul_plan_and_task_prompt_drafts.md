# Development Log: Workflow Overhaul Plan And Task Prompt Drafts

## Entry 1

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_plan_and_task_prompt_drafts
- Task title: Workflow overhaul plan and task prompt drafts
- Status: started
- Affected systems: notes, plans, development logs, document-schema tests, prompt drafts
- Summary: Started a planning-only documentation task to author draft prompt markdown files for the lower two workflow-overhaul tiers so the prompt bundle no longer stops at epic and sub-epic concepts.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_plan_and_task_prompt_drafts.md`
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_and_sub_epic_prompt_drafts.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `AGENTS.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul/draft/prompts -maxdepth 2 -type f | sort`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/nodes/plan.yaml`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/nodes/task.yaml`
- Result: Confirmed that the planning-stage prompt bundle had generic and profile-specific draft files for epic and phase-like tiers only, while the lower-tier profile names existed only in prose.
- Next step: Add `plan/` and `task/` draft prompt files, update the workflow-overhaul note and prompt README, and run the targeted document-schema tests.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_plan_and_task_prompt_drafts
- Task title: Workflow overhaul plan and task prompt drafts
- Status: complete
- Affected systems: notes, plans, development logs, document-schema tests, prompt drafts
- Summary: Added planning-stage markdown prompt drafts for the `plan` tier and `task` tier, including generic baselines and profile-specific variants for authoring, execution, verification, implementation, review, docs, and real E2E work. Updated the workflow-overhaul note and prompt README so the future prompt bundle now covers all four node kinds.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_plan_and_task_prompt_drafts.md`
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_and_sub_epic_prompt_drafts.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The workflow-overhaul planning area now includes reviewable lower-tier prompt drafts without changing the active runtime prompt pack.
- Next step: Review whether the current lower-tier profile vocabulary should stay as full prompt variants or collapse into thinner overlays before any authoritative runtime prompt assets are added.
