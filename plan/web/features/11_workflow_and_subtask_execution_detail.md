# Web Feature 11: Workflow And Subtask Execution Detail

## Goal

Expand the website detail surfaces so operators can inspect stage and subtask execution detail, including current subtask state, attempt history, outcomes, and supporting context.

## Rationale

- Rationale: The current workflow tab stops at task names and subtask counts, which leaves operators unable to inspect what each subtask did, what happened, and what the latest run actually produced.
- Reason for existence: This feature exists to turn the website detail area into a usable execution-inspection surface instead of a high-level summary only.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/02_detail_tabs.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `notes/planning/implementation/execution_orchestration_and_result_capture_decisions.md`
- `AGENTS.md`

## Scope

- Database: reuse durable run, current-subtask, attempt-history, prompt-history, summary-history, and audit records.
- CLI: keep website execution detail aligned with existing operator inspection surfaces for runs, current subtasks, and attempts.
- Daemon: reuse existing current-subtask and subtask-attempt endpoints where possible; add any missing read-model shaping needed for practical browser inspection.
- Website: add stage and subtask detail views under workflow and/or runs tabs so operators can inspect current subtask metadata, attempts, summaries, command results, and relevant context without leaving the browser.
- YAML: not applicable.
- Prompts: expose prompt and summary associations where subtask detail requires them.
- Tests: cover current-subtask rendering, attempt-list rendering, selected-attempt detail, empty/error states, and route/deep-link behavior if attempt selection becomes routable.
- Performance: heavy attempt/context payloads should load on demand rather than inflating the default overview or workflow fetches.
- Notes: update the detail-tab scope notes so they describe which execution surfaces now live in workflow, runs, or a dedicated subtask view.

## Planned Work

1. Freeze the intended detail shape for:
   - workflow stage list
   - current stage marker
   - current subtask detail
   - attempt history
   - selected attempt detail
   - result and summary associations
2. Decide whether subtask inspection belongs in:
   - the workflow tab
   - the runs tab
   - or a new execution subpanel shared by both
3. Reuse current daemon endpoints for:
   - `/api/nodes/{node_id}/subtasks/current`
   - `/api/nodes/{node_id}/subtasks/current/prompt`
   - `/api/nodes/{node_id}/subtasks/current/context`
   - `/api/nodes/{node_id}/subtask-attempts`
   - `/api/subtask-attempts/{attempt_id}`
4. Add bounded UI affordances for expanding task rows into their subtasks and selecting one subtask or attempt for full detail.
5. Extend browser proof to cover real operator inspection of current execution rather than just high-level workflow metadata.

## Notes

- This phase is about read-heavy execution detail, not about introducing browser-side control over every subtask mutation path.
- If the existing daemon payloads are too raw for practical rendering, add a daemon-owned aggregation layer rather than stitching business rules in React.
