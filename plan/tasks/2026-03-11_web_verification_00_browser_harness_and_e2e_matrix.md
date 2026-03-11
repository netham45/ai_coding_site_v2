# Task: Web Verification 00 Browser Harness And E2E Matrix

## Goal

Formally adopt the website browser-test harness and core E2E target matrix based on the harness and Playwright work already implemented.

## Rationale

- Rationale: The harness and E2E target matrix are already embodied in the setup and feature phases, but this prewritten verification phase still needs an explicit authoritative task artifact so the `plan/web` sequence is fully accounted for.
- Reason for existence: This task exists to reconcile the planned browser harness and E2E matrix with the actual implemented mock-daemon and Playwright surface rather than leaving that phase only implicitly satisfied.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/web/verification/00_browser_harness_and_e2e_matrix.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: no new database behavior is introduced; deterministic daemon-presented scenario data remains the planned browser-test substrate.
- CLI: not a primary proving surface for this task.
- Daemon: reconcile the implemented mock-daemon scenario mode and action-capable HTTP test surface with the planned harness note.
- Website: reconcile the implemented Playwright target matrix with the planned browser narratives.
- YAML: not applicable.
- Prompts: include prompt/regeneration coverage in the adopted matrix because it is already browser-proven.
- Tests: rerun the current browser and document proving surface after the harness/matrix note is recorded.
- Performance: no new performance work is planned.
- Notes: record the adopted harness and target matrix in an implementation note so the phase is closed honestly.

## Planned Changes

1. Add the governing task plan and development log for the harness/matrix reconciliation pass.
2. Record the currently adopted browser harness and E2E matrix in an implementation note.
3. Update the task index so this prewritten verification phase is represented explicitly.
4. Rerun the relevant browser and document verification commands.
5. Record the result honestly as a reconciliation/closure pass rather than new feature work.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm run test:e2e
cd frontend && npm run test:unit
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the browser harness and E2E matrix phase has an explicit authoritative task artifact
- an implementation note records the adopted harness and current Playwright target matrix
- the task index includes this phase
- the canonical verification commands are rerun and recorded honestly
- the governing task plan and development log reference each other
