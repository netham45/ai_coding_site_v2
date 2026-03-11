# Web Feature 04: Bounded Action Surface

## Goal

Implement the bounded v1 action surface and generic action catalog.

## Rationale

- Rationale: The website needs an action surface, but it must be daemon-derived and legality-aware rather than a pile of ad hoc buttons.
- Reason for existence: This feature exists to turn bounded safe operator actions into a coherent browser surface with explicit blocked reasons, confirmations, and refresh behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/72_F13_expanded_human_intervention_matrix.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `AGENTS.md`

## Scope

- Database: rely on durable mutation, event, and audit records.
- CLI: keep action semantics aligned with CLI and daemon surfaces.
- Daemon: add or adapt the generic action catalog and use daemon-side legality evaluation.
- YAML: do not move runtime legality into YAML policy mapping.
- Prompts: prompt-update action behavior is included where it intersects with actions.
- Tests: cover action legality, blocked reasons, confirmations, refresh behavior, and action-table completeness.
- Performance: action-state refresh should be targeted, not broad full-page reloads.
- Notes: keep the action table and rubric synchronized with actual implementation.
