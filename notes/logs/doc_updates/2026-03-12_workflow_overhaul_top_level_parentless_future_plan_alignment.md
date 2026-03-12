# Workflow Overhaul Top-Level Parentless Future-Plan Alignment

## Entry 1

- Timestamp: 2026-03-12T09:30:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment
- Task title: Workflow overhaul top-level parentless future-plan alignment
- Status: started
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Began a future-plan-only documentation pass to reconcile the workflow-overhaul bundle with the repository doctrine that top-ness is structural and any node kind may be top-level when its hierarchy definition allows `allow_parentless: true`.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
  - `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/yaml/yaml_schemas_spec_v2.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- Commands and tests run:
  - `rg -n "top-level kind|top-level kinds|allow_parentless|parentless|workflow start --kind|node create --kind|top-level" src tests notes plan flows -S`
  - `sed -n '1,240p' plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/README.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- Result: Confirmed that the authoritative specs and the existing reconciliation plan already state the intended parentless-top-level doctrine clearly, while the workflow-overhaul bundle still reads as epic-rooted by default and lacks explicit future proof obligations for non-epic top-level starts.
- Next step: Update the workflow-overhaul future-plan notes and proof matrix so they explicitly inherit the structural top-level rule and define planned unit, integration, and E2E coverage for any shipped parentless profile set.

## Entry 2

- Timestamp: 2026-03-12T09:55:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment
- Task title: Workflow overhaul top-level parentless future-plan alignment
- Status: complete
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Updated the workflow-overhaul future-plan bundle so it now explicitly preserves the structural `allow_parentless` top-level rule, clarifies that epic-rooted examples are only defaults within the draft bundle, and adds planned bounded, integration, and real-E2E proof expectations for non-epic parentless starts when they are shipped.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment.md`
  - `AGENTS.md`
  - `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/yaml/yaml_schemas_spec_v2.md`
- Commands and tests run:
  - `sed -n '1,240p' plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/README.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Passed: `tests/unit/test_task_plan_docs.py` and `tests/unit/test_document_schema_docs.py` (`13 passed`).
  - Changed files:
    - `plan/tasks/2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment.md`
    - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
    - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
    - `plan/future_plans/workflow_overhaul/prompts/README.md`
    - `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment.md`
  - Next step: If this future direction is promoted into real implementation work later, open the authoritative follow-up against `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md` and the affected feature plans so the code, built-in YAML, and E2E surfaces inherit the same rule.

## Entry 3

- Timestamp: 2026-03-12T10:05:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment
- Task title: Workflow overhaul top-level parentless future-plan alignment
- Status: changed_plan
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Reopened the just-completed future-plan pass after clarifying that the intended future direction is not only that all built-in tiers can start top-level, but that every draft workflow profile should also be startable top-level through its own `applies_to_kind` with no epic wrapper requirement.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_top_level_parentless_future_plan_alignment.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The future-plan bundle now states the stronger intended profile-level top-start rule, and the targeted task-plan plus document-schema tests still pass (`13 passed`).
- Next step: Treat this stronger profile-start rule as part of any later authoritative workflow-profile implementation and proving work.
