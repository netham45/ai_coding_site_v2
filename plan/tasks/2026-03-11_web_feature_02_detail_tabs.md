# Task: Web Feature 02 Detail Tabs

## Goal

Implement the node detail tabs for overview, workflow, runs, summaries, sessions, and provenance using the existing daemon read surfaces.

## Rationale

- Rationale: The explorer shell now provides tree-based navigation, but the main content area still shows placeholders instead of structured node inspection.
- Reason for existence: This task exists to make the website’s read-heavy operator views available as real route-driven tabs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/02_detail_tabs.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/49_F11_operator_history_and_artifact_commands.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`

## Scope

- Database: no schema change is planned in this slice.
- CLI: keep the tab semantics aligned with existing operator inspection surfaces.
- Daemon: reuse current read endpoints rather than inventing a website-only mega-payload.
- Website: implement overview, workflow, runs, summaries, sessions, and provenance tabs with route-driven loading and debug/raw-json toggles.
- YAML: not applicable.
- Prompts: prompt editing/history remains in the next feature phase.
- Tests: cover each tab, tab routing, loading and empty states, and at least one browser deep-link narrative across multiple tabs.
- Performance: heavy tab data should fetch on demand.
- Notes: document which daemon routes each tab reuses and any gaps discovered during implementation.

## Planned Changes

1. Add the governing task plan and development log for the tab slice.
2. Add or extend frontend API modules for overview, workflow, runs, summaries, sessions, and provenance.
3. Replace the node-tab placeholder with route-driven tabs and tab panels.
4. Add shared tab-navigation, data-panel, and raw-json toggle primitives where needed.
5. Extend the mock daemon with deterministic detail-tab responses.
6. Add bounded frontend proof for tab rendering and at least one multi-tab navigation flow.
7. Add Playwright coverage for deep linking and tab switching.
8. Document the actual reused daemon routes and any remaining deferred tab behavior.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- overview, workflow, runs, summaries, sessions, and provenance tabs render real data
- tab routes deep-link correctly
- tabs use shared loading, empty, and error behavior
- a raw-json/debug escape hatch exists without becoming the main presentation
- the reused daemon read surfaces are documented honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
