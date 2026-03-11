# Task: Web Hardening 01 Residual Browser Gap Closure

## Goal

Close the remaining cheap browser-proof gaps identified by the website verification audit using deterministic mock-daemon scenarios.

## Rationale

- Rationale: The audit narrowed the remaining browser gaps to a small set of route and blocked-state proofs that can be covered without inventing new product behavior.
- Reason for existence: This task exists to add explicit browser proof for empty catalog, top-level creation failure, live-candidate-blocked prompt editing, back/forward navigation, and screenshot artifact capture.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/verification/01_missing_test_audit_and_final_verification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`

## Scope

- Database: no new database behavior is introduced.
- CLI: not applicable.
- Daemon: extend the deterministic mock-daemon scenario layer only.
- Website: add browser proof for the named residual route and blocked-state gaps already implemented in the UI.
- YAML: not applicable.
- Prompts: include the live-candidate-blocked prompt editor state.
- Tests: extend Playwright and rerun the affected bounded/browser/doc proving surface.
- Performance: not a focus of this pass.
- Notes: update the verification audit so it reflects the reduced gap set and current screenshot artifact behavior.

## Planned Changes

1. Add the governing task plan and development log for the residual browser-gap pass.
2. Extend the mock-daemon scenarios with empty project, top-level create failure, and live-candidate-blocked prompt states.
3. Add Playwright proof for empty catalog, create failure, live-candidate prompt blocking, and back/forward navigation behavior.
4. Capture explicit browser screenshots for selected review targets in Playwright outputs.
5. Update the final verification audit note to reflect the reduced residual gap list.
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

- empty project catalog has browser proof
- top-level creation failure has browser proof
- live-candidate-blocked prompt editing has browser proof
- route back/forward behavior has browser proof
- screenshot artifacts are captured for at least the selected review targets
- the verification audit note is updated to match the reduced residual gap set
- the governing task plan and development log reference each other
