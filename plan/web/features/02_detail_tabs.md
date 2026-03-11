# Web Feature 02: Detail Tabs

## Goal

Implement the node detail tabs for overview, workflow, runs, summaries, sessions, and provenance.

## Rationale

- Rationale: The website needs structured node inspection surfaces that are easier to use than raw JSON or repeated CLI queries.
- Reason for existence: This feature exists to make the main read-heavy operator views available in-browser with explicit route, loading, empty, and error behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/49_F11_operator_history_and_artifact_commands.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `AGENTS.md`

## Scope

- Database: rely on existing durable history and audit data.
- CLI: keep tab concepts aligned with operator inspection surfaces.
- Daemon: reuse or adapt existing detail/history/read-model routes.
- YAML: not applicable.
- Prompts: prompt history is handled more deeply in the prompt feature plan.
- Tests: cover each tab, deep-link behavior, and shared loading/empty/error handling.
- Performance: detail tabs should fetch on demand rather than overfetching.
- Notes: keep tab coverage explicit rather than implying all tabs are interchangeable.
