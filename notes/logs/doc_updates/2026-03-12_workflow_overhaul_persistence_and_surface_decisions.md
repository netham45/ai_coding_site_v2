# Workflow Overhaul Persistence And Surface Decisions

## Entry 1

- Timestamp: 2026-03-12T11:05:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_persistence_and_surface_decisions
- Task title: Workflow overhaul persistence and surface decisions
- Status: started
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Began a future-plan-only clarification pass to turn the current workflow-overhaul planning questions around profile persistence, layout timing, compiled-state freezing, database storage, top-level built-in posture, operator inspection surfaces, workflow brief scope, and prompt-bundle promotion into explicit decisions.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_persistence_and_surface_decisions.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `notes/specs/database/database_schema_spec_v2.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/db/models.py`
- Commands and tests run:
  - `rg -n "selected workflow profile|layout_id|node types|node kinds --verbose|workflow brief|compile_context|default_workflow_profile|supported_workflow_profiles|parentless" plan/future_plans/workflow_overhaul notes/specs src/aicoding/db/models.py -S`
  - `sed -n '1,320p' src/aicoding/db/models.py`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- Result: In progress. The current code and notes are enough to record concrete future-plan decisions, especially around compile-context storage and the split between durable columns and richer JSON payloads.
- Next step: Write the dedicated future-plan decision note, update the breakdown note to reference the decisions, and run the targeted document-schema tests.

## Entry 2

- Timestamp: 2026-03-12T11:25:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_persistence_and_surface_decisions
- Task title: Workflow overhaul persistence and surface decisions
- Status: complete
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Added a dedicated future-plan decision note for workflow-profile persistence, layout timing, compiled-state freezing, database storage split, parentless built-in kinds, operator inspection surfaces, workflow brief scope, and prompt-bundle promotion, and updated the plan-family breakdown to treat those items as settled future direction.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_persistence_and_surface_decisions.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `notes/specs/database/database_schema_spec_v2.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/db/models.py`
- Commands and tests run:
  - `rg -n "selected workflow profile|layout_id|node types|node kinds --verbose|workflow brief|compile_context|default_workflow_profile|supported_workflow_profiles|parentless" plan/future_plans/workflow_overhaul notes/specs src/aicoding/db/models.py -S`
  - `sed -n '1,320p' src/aicoding/db/models.py`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Passed: `tests/unit/test_task_plan_docs.py` and `tests/unit/test_document_schema_docs.py` (`13 passed`).
  - Added:
    - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
    - `plan/tasks/2026-03-12_workflow_overhaul_persistence_and_surface_decisions.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_persistence_and_surface_decisions.md`
  - Updated:
    - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
    - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- Next step: Use these recorded future-direction decisions as fixed inputs when opening later authoritative workflow-profile implementation plans, unless a deeper code or schema contradiction is discovered.
