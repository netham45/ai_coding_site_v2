# Web Feature 00: Project Bootstrap And Selection

## Goal

Implement project discovery, project selection, and top-level creation entry behavior for the website.

## Rationale

- Rationale: The website needs an authoritative project context before any tree or detail surface can be useful.
- Reason for existence: This feature exists to make project selection and top-level workflow entry first-class browser flows.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `AGENTS.md`

## Scope

- Database: no direct schema work expected by default.
- CLI: keep project and top-level creation semantics aligned with CLI equivalents.
- Daemon: add or adapt project catalog and top-level creation HTTP surfaces.
- YAML: not applicable.
- Prompts: support operator-entered top-level prompt input.
- Tests: cover project catalog, creation validation, creation success, and redirect behavior.
- Performance: project bootstrap and creation should feel immediate at operator scale.
- Notes: keep project-selection and creation notes aligned with actual backend behavior.
