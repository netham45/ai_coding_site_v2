# Task: Web Verification 03 V1 Action And Shared-State Browser Closure

## Goal

Close the remaining browser-proof gaps for the agreed v1 action table and the shared loading, empty, and error states across the main operator views.

## Rationale

- Rationale: The website audit still names several action flows and shared UI states as only indirectly or partially browser-proven.
- Reason for existence: This task exists to convert those residual verification gaps into explicit deterministic browser proof so the website status can be described more precisely.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/verification/01_missing_test_audit_and_final_verification.md`
- `plan/web/verification/03_v1_action_and_shared_state_browser_closure.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`
- `notes/planning/implementation/frontend_website_browser_harness_matrix_adoption.md`

## Scope

- Database: no new database behavior; this pass is browser-proof closure over deterministic daemon-shaped fixtures.
- CLI: not applicable.
- Daemon: extend the mock-daemon scenario surface so the remaining v1 browser narratives can execute through normal HTTP contracts.
- Website: add Playwright proof for the remaining agreed action flows and representative shared-state surfaces.
- YAML: not applicable.
- Prompts: include explicit empty/loading/error prompt-surface proof.
- Tests: add Playwright coverage and rerun the affected frontend/doc proving surface.
- Performance: keep the new shared-state loading tests deterministic with bounded artificial delays.
- Notes: update the verification audit and harness matrix note to reflect the stronger browser-proof coverage honestly.

## Planned Changes

1. Add the governing task plan and development log for verification phase 03.
2. Extend mock-daemon routing with deterministic exact-route overrides for delayed and failing responses.
3. Add a dedicated action-matrix scenario that browser-proves:
   - `pause_run`
   - `resume_run`
   - `session_attach`
   - `session_resume`
   - `session_provider_resume`
   - `reconcile_children:*`
   - `regenerate_node`
4. Add representative shared-state browser scenarios for projects, tree, actions, and prompts covering loading, empty, and error paths.
5. Update the final verification audit and harness adoption note so they reflect the new browser-proof map.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npx playwright test tests/e2e/action-matrix.spec.js tests/e2e/residual-gaps.spec.js tests/e2e/project-selector-context.spec.js tests/e2e/smoke.spec.js tests/e2e/coverage-gaps.spec.js tests/e2e/tree-filters.spec.js
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- each remaining agreed v1 browser-owned action has explicit Playwright execution proof
- representative loading, empty, and error states are browser-proven on projects, tree, actions, and prompts surfaces
- the verification audit no longer lists those action and shared-state gaps as unproven
- the browser harness note reflects the stronger matrix honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their results are recorded honestly
