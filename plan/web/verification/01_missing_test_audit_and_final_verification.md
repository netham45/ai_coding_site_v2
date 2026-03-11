# Web Verification 01: Missing-Test Audit And Final Verification

## Goal

Perform the final browser-side verification sweep, including explicit audit for missing tests and untested flows.

## Rationale

- Rationale: Final website verification should not stop at "Playwright ran"; it needs an explicit accounting of which routes, views, actions, and visual states are covered.
- Reason for existence: This phase exists to prevent the website effort from claiming completion while still carrying silent browser-side testing gaps.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/verification/00_browser_harness_and_e2e_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `AGENTS.md`

## Scope

- Database: verify durable browser-visible mutations and histories through the real runtime where applicable.
- CLI: not primary, but shared browser/CLI semantics should still agree.
- Daemon: verify the final browser flows against daemon-owned behavior.
- YAML: not applicable.
- Prompts: verify prompt-edit and prompt-history flows as part of browser coverage.
- Tests: run final bounded/browser/E2E proof and explicit missing-test audit.
- Performance: note any browser-proof bottlenecks discovered during verification.
- Notes: record residual gaps honestly rather than implying full closure.
