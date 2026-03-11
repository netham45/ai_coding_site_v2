# Task: Web Verification 01 Missing-Test Audit And Final Verification

## Goal

Perform the planned browser-side verification sweep, including an explicit audit of tested and untested website routes, views, tabs, actions, and visual states.

## Rationale

- Rationale: Final website verification cannot stop at "Playwright passed once"; it needs an explicit accounting of what the browser proof covers and what it still does not cover.
- Reason for existence: This task exists to turn the final verification checklist into a concrete audited artifact with honest residual gaps instead of vague confidence claims.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/verification/01_missing_test_audit_and_final_verification.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: no new database behavior is introduced in this audit slice.
- CLI: not a primary verification surface for this task.
- Daemon: verify the current browser proof still runs against daemon-owned models and routes.
- Website: audit route/view/tab/action/browser coverage and name residual gaps explicitly.
- YAML: not applicable.
- Prompts: include prompt-history and prompt-regeneration proof status in the audit.
- Tests: rerun the current bounded/browser/doc proving surface and record what remains untested.
- Performance: note any verification bottlenecks discovered during the sweep.
- Notes: produce a concrete coverage audit note rather than leaving the final verification checklist abstract.

## Planned Changes

1. Add the governing task plan and development log for the verification sweep.
2. Audit the implemented route, tab, and action surfaces against the current bounded and Playwright tests.
3. Write a concrete verification audit note with explicit covered and uncovered surfaces.
4. Define screenshot and visual-review targets for the current v1 browser scope.
5. Rerun the canonical bounded/browser/document verification commands.
6. Record the result honestly, including residual gaps that still need future proof.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/integration/test_web_project_bootstrap_api.py -q
python3 -m pytest tests/integration/test_web_explorer_tree_api.py -q
python3 -m pytest tests/integration/test_web_actions_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a concrete browser verification audit note exists
- the audit explicitly maps current routes, tabs, actions, and shared primitives to their proof surfaces
- the audit explicitly names residual untested flows instead of hiding them
- screenshot and visual-review targets are defined for the current website scope
- the canonical verification commands are rerun and recorded honestly
- the governing task plan and development log reference each other
