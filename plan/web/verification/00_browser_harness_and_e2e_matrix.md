# Web Verification 00: Browser Harness And E2E Matrix

## Goal

Define and adopt the browser-test harness and core E2E target matrix for the website effort.

## Rationale

- Rationale: Browser verification only becomes enforceable if the daemon-backed test harness and major E2E targets are fixed before implementation gets too far ahead.
- Reason for existence: This phase exists to prevent the website effort from shipping many UI surfaces without a realistic daemon-backed Playwright harness or explicit end-to-end targets.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `AGENTS.md`

## Scope

- Database: use deterministic seeded or scenario-backed state where required by the harness.
- CLI: not the primary surface, though shared auth/runtime assumptions still matter.
- Daemon: run a real daemon HTTP process or equivalent deterministic scenario mode.
- YAML: not applicable.
- Prompts: cover prompt-related browser flows where they are part of v1.
- Tests: define harness shape and explicit Playwright target coverage.
- Performance: browser scenarios should be practical to run repeatedly.
- Notes: keep harness and verification checklist notes aligned with the actual browser proving strategy.
