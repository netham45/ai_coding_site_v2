# Web Verification 03: V1 Action And Shared-State Browser Closure

## Goal

Close the remaining browser-proof gaps for the agreed v1 action surface and the shared loading, empty, and error state patterns so the website is not relying on partial browser coverage for those required flows.

## Rationale

- Rationale: The current audit still lists several agreed v1 actions as daemon/API-proven but not individually browser-executed, and the shared UI primitives still lack dedicated browser proof across multiple states.
- Reason for existence: This phase exists to stop the website from claiming v1 browser readiness while some required action flows and shared-state presentations are still only indirectly or partially proven.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/verification/01_missing_test_audit_and_final_verification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: verify browser-executed mutations against real durable state where applicable.
- CLI: not primary, but browser-triggered mutations should remain semantically consistent with existing operator surfaces.
- Daemon: exercise the remaining agreed v1 action routes through browser-driven or browser-adjacent proof rather than stopping at API-only assertions.
- YAML: not applicable.
- Prompts: include prompt-regeneration browser proof only where it intersects with the agreed v1 action inventory.
- Tests: add dedicated browser proof for the remaining agreed v1 actions and for representative loading, empty, and error states across major views.
- Performance: note any action-refresh or state-transition latency discovered while closing the browser-proof matrix.
- Notes: update the final verification audit so the remaining gaps are narrowed or closed honestly.

## Verify

- Each agreed v1 action in the action table has explicit browser execution proof or a documented reason it is not browser-owned.
- Browser success and blocked/error states are covered for the remaining agreed action flows.
- Shared `LoadingState`, `EmptyState`, and `ErrorState` behaviors are browser-proven intentionally rather than only as incidental side effects.
- The audit no longer relies on vague “broader partial” language for the remaining agreed v1 action set.

## Tests

- Extend deterministic browser scenarios and Playwright coverage for:
  - `pause_run`
  - `resume_run`
  - `session_attach`
  - `session_resume`
  - `session_provider_resume`
  - `reconcile_children:*`
  - `regenerate_node`
- Add dedicated browser passes for representative loading, empty, and error states on the projects screen, tree/detail shell, and action/prompt surfaces.
- Rerun the website audit and update it with the resulting browser-proof map.

## Notes

- This phase is about browser-proof closure for already agreed v1 behavior, not expanding the action set further.
- If any supposedly agreed v1 action turns out not to belong in the browser after implementation review, that change must be recorded as a scope correction rather than silently omitted.
