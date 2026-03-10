# Development Log: Workflow Overhaul Epic And Sub-Epic Prompt Drafts

## Entry 1

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_epic_and_sub_epic_prompt_drafts
- Task title: Workflow overhaul epic and sub-epic prompt drafts
- Status: started
- Affected systems: notes, plans, development logs, document-schema tests, prompt drafts
- Summary: Started a planning-only documentation task to author draft prompt markdown files for the epic and sub-epic tiers of the workflow-overhaul design.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_and_sub_epic_prompt_drafts.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `find src/aicoding/resources/prompts/packs/default -maxdepth 2 -type f | sort`
  - `find plan/future_plans/workflow_overhaul -maxdepth 3 -type f | sort`
- Result: The current active prompt pack and the current workflow-overhaul planning area were reviewed. No dedicated planning-stage prompt files existed yet for the proposed profile-aware epic and sub-epic surfaces.
- Next step: Add draft prompt markdown files under the workflow-overhaul planning area, update the note to reference them, and run the targeted document-schema tests.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_epic_and_sub_epic_prompt_drafts
- Task title: Workflow overhaul epic and sub-epic prompt drafts
- Status: complete
- Affected systems: notes, plans, development logs, document-schema tests, prompt drafts
- Summary: Added planning-stage markdown prompt drafts for the epic tier and sub-epic tier, including generic baselines and profile-specific variants for planning, feature, review, documentation, discovery, implementation, remediation, and real-E2E work. Updated the workflow-overhaul note to reference the new prompt-draft directory.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_and_sub_epic_prompt_drafts.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The workflow-overhaul planning area now contains concrete `.md` prompt files for epic and sub-epic stages without altering the active runtime prompt pack.
- Next step: Draft the next tier of planning-stage prompt files for `plan` and `task`, then review whether the current profile vocabulary needs refinement before promoting any of these prompts into authoritative implementation-facing notes.
