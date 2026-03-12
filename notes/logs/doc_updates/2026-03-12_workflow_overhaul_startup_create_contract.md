# Workflow Overhaul Startup And Create Contract

## Entry 1

- Timestamp: 2026-03-12T12:10:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_startup_create_contract
- Task title: Workflow overhaul startup and create contract
- Status: started
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Began the first concrete workflow-overhaul contract pass by focusing on profile-aware startup and node creation semantics, grounded in the current daemon-owned startup flow and CLI create/start surfaces.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_startup_create_contract.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/daemon/workflow_start.py`
  - `src/aicoding/cli/handlers.py`
  - `src/aicoding/daemon/models.py`
- Commands and tests run:
  - `sed -n '1,260p' src/aicoding/daemon/workflow_start.py`
  - `sed -n '140,240p' src/aicoding/cli/handlers.py`
  - `sed -n '300,360p' src/aicoding/daemon/models.py`
  - `sed -n '150,180p' notes/specs/cli/cli_surface_spec_v2.md`
  - `sed -n '55,120p' notes/specs/runtime/node_lifecycle_spec_v2.md`
- Result: In progress. The current startup path is narrow enough that a concrete future contract can be written without speculation, and the version-scoped profile persistence decision from the prior planning pass provides a stable base.
- Next step: Author the future-plan contract note and run the targeted task-plan/document-schema tests.

## Entry 2

- Timestamp: 2026-03-12T12:25:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_startup_create_contract
- Task title: Workflow overhaul startup and create contract
- Status: complete
- Affected systems: notes, plans, development logs, document consistency tests
- Summary: Added a dedicated future-plan startup/create contract note that freezes the intended profile-aware mutation semantics, version-scoped profile persistence, structural top-level legality, compact mutation-response posture, and CLI direction for later authoritative planning.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_startup_create_contract.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
  - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/daemon/workflow_start.py`
  - `src/aicoding/cli/handlers.py`
  - `src/aicoding/daemon/models.py`
- Commands and tests run:
  - `sed -n '1,260p' src/aicoding/daemon/workflow_start.py`
  - `sed -n '140,220p' src/aicoding/cli/handlers.py`
  - `sed -n '300,360p' src/aicoding/daemon/models.py`
  - `sed -n '140,220p' notes/specs/cli/cli_surface_spec_v2.md`
  - `sed -n '55,120p' notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Passed: `tests/unit/test_task_plan_docs.py` and `tests/unit/test_document_schema_docs.py` (`13 passed`).
  - Added:
    - `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
    - `plan/tasks/2026-03-12_workflow_overhaul_startup_create_contract.md`
    - `notes/logs/doc_updates/2026-03-12_workflow_overhaul_startup_create_contract.md`
  - Updated:
    - `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- Next step: Draft the next concrete adjacent contract, likely either the workflow-profile YAML/schema contract or the profile-aware materialization contract.
