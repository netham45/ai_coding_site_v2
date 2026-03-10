# Development Log: Workflow Overhaul Epic Profiles And Tier Prompt Note

## Entry 1

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_epic_profiles_and_tier_prompts_note
- Task title: Workflow overhaul epic profiles and tier prompt note
- Status: started
- Affected systems: notes, plans, development logs, document-schema tests
- Summary: Started a documentation task to expand the workflow-overhaul future-plan note with concrete epic-style profile YAML proposals, tier contracts, and baseline prompt drafts.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_profiles_and_tier_prompts_note.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `notes/explorations/original_concept.md`
  - `notes/planning/implementation/project_development_flow_doctrine.md`
  - `notes/planning/implementation/implementation_slicing_plan.md`
  - `notes/planning/implementation/configurable_node_hierarchy_decisions.md`
  - `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "workflow_overhaul|epic|phase|plan|task" notes plan`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `sed -n '1,260p' notes/explorations/original_concept.md`
  - `sed -n '1,260p' notes/planning/implementation/project_development_flow_doctrine.md`
  - `sed -n '1,260p' notes/planning/implementation/implementation_slicing_plan.md`
  - `sed -n '1,260p' notes/planning/implementation/configurable_node_hierarchy_decisions.md`
  - `sed -n '1,260p' notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
  - `sed -n '1,260p' notes/specs/architecture/code_vs_yaml_delineation.md`
  - `sed -n '1,260p' notes/specs/prompts/prompt_library_plan.md`
- Result: The current notes and assets were reviewed. The main gaps are lack of semantic profile selection for epics, lack of richer child-role metadata in layouts, and overly generic tier prompts.
- Next step: Update the workflow-overhaul future-plan note with explicit YAML proposals, tier definitions, prompt drafts, and implementation guardrails, then run document-schema tests.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: workflow_overhaul_epic_profiles_and_tier_prompts_note
- Task title: Workflow overhaul epic profiles and tier prompt note
- Status: complete
- Affected systems: notes, plans, development logs, document-schema tests
- Summary: Expanded the workflow-overhaul future-plan note into a concrete design draft covering profile-aware epics, proposed YAML families and fields, explicit tier contracts, profile-specific behavior, and baseline per-tier prompts for later review and iteration.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_workflow_overhaul_epic_profiles_and_tier_prompts_note.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `notes/explorations/original_concept.md`
  - `notes/planning/implementation/project_development_flow_doctrine.md`
  - `notes/planning/implementation/implementation_slicing_plan.md`
  - `notes/planning/implementation/configurable_node_hierarchy_decisions.md`
  - `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
  - `notes/specs/architecture/code_vs_yaml_delineation.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The governing task plan, development log, and expanded workflow-overhaul note now exist together, and the future-plan note contains the requested YAML proposals and prompt drafts.
- Next step: If this direction is accepted, promote the tier contracts and workflow-profile model into authoritative implementation notes and task plans before touching runtime YAML, prompt assets, or compiler code.
