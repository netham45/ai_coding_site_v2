# Web Feature 03: Prompts And Regeneration Flow

## Goal

Implement prompt history, prompt editing, and supersede-plus-regenerate flow for the website.

## Rationale

- Rationale: Prompt editing is a high-value operator mutation and is tightly coupled to regeneration semantics.
- Reason for existence: This feature exists to make prompt revision and regeneration possible from the browser without clobbering node history.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `AGENTS.md`

## Scope

- Database: rely on durable versioning, prompt history, and regeneration records.
- CLI: keep prompt-edit and regeneration semantics aligned with CLI/runtime behavior.
- Daemon: use supersede semantics and regeneration surfaces; add legality metadata if needed.
- YAML: not applicable.
- Prompts: this feature directly covers prompt input and history behavior.
- Tests: cover prompt history, edit states, discard/keep-editing/confirm, and post-action refresh.
- Performance: prompt flows should refresh only affected surfaces.
- Notes: keep prompt/regeneration semantics aligned with version-preserving supersession.
