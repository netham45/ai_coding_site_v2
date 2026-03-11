# Task: Web Hardening 00 Browser Gap Closure

## Goal

Close the highest-value remaining browser-proof gaps discovered by the website verification audit.

## Rationale

- Rationale: The verification audit named several browser gaps explicitly; the cheapest useful next step is to close the route/tab/action gaps that already have deterministic mock-daemon support.
- Reason for existence: This task exists to improve the browser proving surface without inventing new website behavior, focusing on deep-link coverage and blocked-action proof for already-implemented routes and tabs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/verification/01_missing_test_audit_and_final_verification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`

## Scope

- Database: no new database behavior is introduced.
- CLI: not applicable.
- Daemon: no new daemon feature behavior is planned; reuse deterministic mock-daemon scenarios.
- Website: add browser proof for currently implemented workflow, summaries, and sessions tabs plus a blocked action state.
- YAML: not applicable.
- Prompts: not the focus of this gap-closure slice.
- Tests: extend Playwright coverage only.
- Performance: no meaningful performance work is planned.
- Notes: update the verification audit so it reflects the narrower remaining gap list after this pass.

## Planned Changes

1. Add the governing task plan and development log for the browser gap-closure pass.
2. Extend Playwright with a deterministic deep-link scenario using the existing healthy-tree mock daemon state.
3. Add browser proof for workflow, summaries, and sessions tabs.
4. Add browser proof for a blocked action state.
5. Update the verification audit note to reflect the reduced residual gap set.
6. Run the affected frontend/browser and document verification commands.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:e2e
cd frontend && npm run test:unit
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- workflow tab has browser proof
- summaries tab has browser proof
- sessions tab has browser proof
- at least one blocked action state has browser proof
- the verification audit note is updated to match the improved coverage
- the governing task plan and development log reference each other
