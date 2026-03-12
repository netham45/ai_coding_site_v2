# Task: Workflow Overhaul Web UI Integration Plan

## Goal

Review the current web UI implementation and the existing frontend future-plan bundle in the context of workflow-overhaul, then add a future-plan note that defines the website UI changes and dependencies workflow-profile support will require.

## Rationale

- Rationale: The workflow-overhaul bundle was written before the current website planning and implementation work matured, so it does not yet account for how profile-aware startup, inspection, and materialization should surface in the browser.
- Reason for existence: This task exists to close that planning gap by connecting the workflow-overhaul future direction to the existing web UI future-plan artifacts and the real frontend codebase.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/web/features/09_project_multi_root_navigation_and_creation_persistence.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`

## Scope

- Database: no direct schema change in this planning pass, but the note should call out browser-visible durable data that workflow-overhaul will require.
- CLI: not directly changed here, but the website plan should remain aligned with CLI/runtime surfaces rather than inventing browser-only orchestration concepts.
- Daemon: review the current website-facing routes and identify future route/response additions needed for workflow-profile-aware UI.
- Website: review the current frontend structure and the existing web future-plan bundle, then define the browser impact of workflow-overhaul.
- YAML: not directly changed here beyond noting that the browser should consume daemon-resolved profile/layout state rather than raw YAML logic.
- Prompts: note where prompt-stack and workflow-brief data will need browser inspection surfaces later.
- Tests: identify the bounded browser and real browser/E2E impact of workflow-overhaul on the web plan.
- Performance: call out any high-frequency browser reads that should stay compact even if richer profile surfaces are added.
- Notes: add the workflow-overhaul/web-ui integration plan and thread it into the existing workflow-overhaul future-plan bundle.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a workflow-overhaul future-plan note exists for website UI integration
- the note references the existing frontend future-plan bundle explicitly
- the workflow-overhaul bundle references the web UI integration note
- the required development log records the reviewed files, commands run, and results
