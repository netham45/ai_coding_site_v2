# Workflow Overhaul Code Alignment And Plan Coverage Audit

## Entry 1

- Timestamp: 2026-03-12T23:14:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_code_alignment_and_plan_coverage_audit
- Task title: Workflow-overhaul code alignment and plan coverage audit
- Status: started
- Affected systems: database planning context, CLI planning context, daemon planning context, YAML planning context, prompts planning context, development logs, document consistency tests
- Summary: Began auditing the executable workflow-overhaul draft plans against the current code so the plans can reference the real files they will need to change and call out current coverage gaps.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_code_alignment_and_plan_coverage_audit.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/README.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `rg -n "workflow_profile|compiled_tasks|compiled_subtasks|materializ|checklist|prompt_ref|workflow brief|node profiles|node types" src`
  - `sed -n '1120,1260p' src/aicoding/daemon/workflows.py`
  - `sed -n '180,320p' src/aicoding/daemon/materialization.py`
  - `sed -n '1,220p' src/aicoding/daemon/workflow_start.py`
- Result: In progress. The draft plans need explicit current-code sections, and there are still future-plan notes that only exist as supporting inputs instead of dedicated executable plan slices.
- Next step: Patch the executable draft plans with code references and gap notes, update the draft plan index with the missing-coverage summary, rerun document tests, and record the final result.

## Entry 2

- Timestamp: 2026-03-12T23:22:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_code_alignment_and_plan_coverage_audit
- Task title: Workflow-overhaul code alignment and plan coverage audit
- Status: complete
- Affected systems: database planning context, CLI planning context, daemon planning context, YAML planning context, prompts planning context, development logs, document consistency tests
- Summary: Added current-code references and current-gap sections to the executable workflow-overhaul draft plans and updated the draft plan index with the missing-coverage summary for the future-plan note bundle.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_code_alignment_and_plan_coverage_audit.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/README.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `rg -n "workflow_profile|compiled_tasks|compiled_subtasks|materializ|checklist|prompt_ref|workflow brief|node profiles|node types" src`
  - `find frontend/src -maxdepth 3 -type f | sort`
  - `find tests -maxdepth 3 -type f | sort | rg 'e2e|workflow|materialization|compile|start' -n -`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - Updated the executable draft setup and feature plans under `draft_setup_plans/` and `draft_feature_plans/` with `Relevant Current Code` and `Current Gaps` sections.
  - Updated `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md` with the current known coverage gaps in the draft queue.
  - Updated `plan/tasks/README.md`.
  - Verification passed: `13 passed in 2.97s`
- Next step: If desired, the next cleanup pass should add a dedicated workflow-profile website UI execution slice and split migration/backfill work into a narrower executable draft plan.
