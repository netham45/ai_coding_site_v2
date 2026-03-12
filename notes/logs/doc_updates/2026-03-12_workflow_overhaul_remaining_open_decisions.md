# Workflow Overhaul Remaining Open Decisions

## Entry 1

- Timestamp: 2026-03-12T11:40:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_remaining_open_decisions
- Task title: Workflow overhaul remaining open decisions
- Status: started
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Began a future-plan clarification pass to close the remaining open workflow-overhaul decisions around migration shape, `effective_layout_id` storage, inspection-route posture, compile-context schema, and generated-layout precedence.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_remaining_open_decisions.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
  - `notes/specs/database/database_schema_spec_v2.md`
  - `src/aicoding/db/models.py`
  - `src/aicoding/daemon/materialization.py`
- Commands and tests run:
  - `rg -n "effective_layout_id|layout_id|workflow brief|node types|node profiles|generated layout|compile_context|resolved_yaml" plan/future_plans/workflow_overhaul notes/specs src/aicoding/db/models.py src/aicoding/daemon/materialization.py -S`
  - `sed -n '1,320p' src/aicoding/db/models.py`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- Result: In progress. The current implementation and draft notes are enough to make these decisions explicit without forcing premature implementation detail into the future-plan bundle.
- Next step: Update the decision note and breakdown note, then run the targeted document-schema tests.

## Entry 2

- Timestamp: 2026-03-12T11:55:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_remaining_open_decisions
- Task title: Workflow overhaul remaining open decisions
- Status: complete
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Closed the remaining workflow-overhaul future-plan questions by recording explicit decisions for additive migration posture, deferring a first-class `effective_layout_id` column, keeping inspection routes additive and non-overlapping, structuring compile-context into stable sections, and giving registered generated layouts precedence over profile defaults once registered.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_remaining_open_decisions.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
  - `notes/specs/database/database_schema_spec_v2.md`
  - `src/aicoding/db/models.py`
  - `src/aicoding/daemon/materialization.py`
- Commands and tests run:
  - `rg -n "effective_layout_id|layout_id|workflow brief|node types|node profiles|generated layout|compile_context|resolved_yaml" plan/future_plans/workflow_overhaul notes/specs src/aicoding/db/models.py src/aicoding/daemon/materialization.py -S`
  - `sed -n '1500,1565p' notes/specs/database/database_schema_spec_v2.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
  - `sed -n '1,320p' plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Passed: `tests/unit/test_task_plan_docs.py` and `tests/unit/test_document_schema_docs.py` (`13 passed`).
  - Updated:
    - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
    - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - Added:
    - `plan/tasks/2026-03-12_workflow_overhaul_remaining_open_decisions.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_remaining_open_decisions.md`
- Next step: The remaining open work is now mostly detailed contract authoring and later authoritative-plan decomposition, not major directional ambiguity.
