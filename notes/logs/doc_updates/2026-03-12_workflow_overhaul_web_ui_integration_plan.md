# Workflow Overhaul Web UI Integration Plan

## Entry 1

- Timestamp: 2026-03-12T12:40:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_web_ui_integration_plan
- Task title: Workflow overhaul web UI integration plan
- Status: started
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Began a future-plan review to connect the workflow-overhaul bundle to the current website UI code and the existing frontend future-plan notes so browser implications are explicitly planned rather than left implicit.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_web_ui_integration_plan.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- Commands and tests run:
  - `rg -n "top-level|workflow|profile|tree|detail|project" frontend/src src/aicoding/daemon plan/future_plans/frontend_website_ui -S`
  - `rg --files frontend/src | sort`
  - `sed -n '1,260p'` on the main frontend future-plan notes and current frontend route/data-access files under review
- Result: In progress. The frontend future-plan bundle already has strong top-level creation and explorer-shell planning, but it predates the newer workflow-overhaul contract decisions and does not yet define browser surfaces for workflow profiles, `workflow brief`, or node-context type/profile inspection.
- Next step: Finish the frontend review, write the web UI integration note, and thread it into the workflow-overhaul bundle.

## Entry 2

- Timestamp: 2026-03-12T13:05:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_web_ui_integration_plan
- Task title: Workflow overhaul web UI integration plan
- Status: complete
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Added a workflow-overhaul/web-ui integration note that connects the existing frontend future-plan bundle to workflow-profile-aware startup, tree rendering, detail tabs, data-access surfaces, and browser testing, and threaded that note back into the workflow-overhaul bundle.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_web_ui_integration_plan.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- Commands and tests run:
  - `rg -n "top-level|workflow|profile|tree|detail|project" frontend/src src/aicoding/daemon plan/future_plans/frontend_website_ui -S`
  - `rg --files frontend/src | sort`
  - `sed -n '1,260p' frontend/src/routes/router.js`
  - `sed -n '1,260p' frontend/src/routes/pages.js`
  - `sed -n '1,260p' frontend/src/lib/api/topLevelCreation.js`
  - `sed -n '1,260p' frontend/src/lib/api/tree.js`
  - `sed -n '1,260p' frontend/src/components/detail/NodeDetailTabs.js`
  - `sed -n '1,260p' frontend/src/components/shell/HierarchyTree.js`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Passed: `tests/unit/test_task_plan_docs.py` and `tests/unit/test_document_schema_docs.py` (`13 passed`).
  - Added:
    - `plan/future_plans/workflow_overhaul/2026-03-12_web_ui_integration_plan.md`
    - `plan/tasks/2026-03-12_workflow_overhaul_web_ui_integration_plan.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_web_ui_integration_plan.md`
  - Updated:
    - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
    - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- Next step: If this continues, the next useful concrete workflow-overhaul contract is likely the workflow-profile YAML/schema contract or the profile-aware browser creation contract that extends the existing frontend top-level creation contract.
