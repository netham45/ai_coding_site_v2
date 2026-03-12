# Task: Web Feature 11 Workflow And Subtask Execution Detail

## Goal

Expand the website workflow detail surface so operators can inspect compiled subtasks, current execution state, prompt/context payloads, and attempt history from the browser.

## Rationale

- Rationale: The current workflow tab stops at task names and subtask counts, which hides the actual execution detail operators need when a node is running or blocked inside a specific subtask.
- Reason for existence: This task exists to align the website workflow tab with the daemon's existing subtask and attempt inspection contracts rather than leaving execution detail available only through CLI and raw daemon APIs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/11_workflow_and_subtask_execution_detail.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `notes/planning/implementation/frontend_website_detail_tabs_decisions.md`
- `notes/planning/implementation/execution_orchestration_and_result_capture_decisions.md`

## Scope

- Database: reuse durable compiled workflow, current-subtask, prompt, context, summary, and subtask-attempt records.
- CLI: no new CLI behavior is planned, but browser-presented execution detail must remain aligned with existing `workflow`, `subtask`, and run inspection commands.
- Daemon: reuse existing read routes for current subtask, current prompt/context, and attempt history/detail unless implementation proves an additional aggregation layer is required.
- Website: replace the workflow tab's flat task summary with expandable task and subtask detail, current execution context, and attempt inspection.
- YAML: not applicable.
- Prompts: expose prompt associations for the selected current subtask where the daemon already records them.
- Tests: extend bounded checks and browser E2E proof for task expansion, current-subtask detail, attempt selection, and empty-state behavior.
- Performance: load attempt-detail lazily so the default workflow tab does not fetch every attempt payload eagerly.
- Notes: update the detail-tab implementation note so it records which execution detail now lives under the workflow tab.

## Planned Changes

1. Add the task plan and development log for feature 11.
2. Extend the frontend workflow API layer with:
   - current subtask
   - current subtask prompt
   - current subtask context
   - subtask attempt catalog
   - selected subtask attempt detail
3. Replace the workflow tab's flat task list with:
   - expandable task rows
   - subtask rows with current markers
   - a selected subtask detail card
   - a current execution detail card
   - attempt history plus selected attempt detail
4. Extend the mock daemon and scenario data so browser tests can prove real subtask inspection behavior.
5. Update the detail-tab note and feature log with the actual execution-surface contract.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npx playwright test tests/e2e/coverage-gaps.spec.js tests/e2e/smoke.spec.js
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow tab exposes more than task names and subtask counts
- operators can expand a task and inspect at least one compiled subtask's metadata in the browser
- current execution detail includes current subtask, prompt/context associations, and attempt history when the daemon exposes them
- selected attempt detail loads on demand rather than inflating every workflow fetch
- bounded and browser proof cover task expansion and execution-detail inspection honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
