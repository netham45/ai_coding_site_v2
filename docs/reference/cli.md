---
doc_type: reference
verified_against:
  - cli
flow_ids:
  - 01_create_top_level_node_flow
  - 06_inspect_state_and_blockers_flow
  - 07_pause_resume_and_recover_flow
  - 12_query_provenance_and_docs_flow
command_paths:
  - admin doctor
  - admin print-settings
  - admin auth-token
  - admin db ping
  - admin db upgrade
  - admin db check-schema
  - workflow start
  - workflow current
  - node show
  - node blockers
  - session bind
  - session show-current
  - session recover
  - session provider-resume
  - docs list
  - docs show
---

# CLI Reference

This file is the operator/reference entrypoint for the current CLI surface used most often during bootstrap, inspection, runtime work, and documentation inspection.

## Bootstrap And Admin

- `admin doctor`
- `admin print-settings`
- `admin auth-token`
- `admin db ping`
- `admin db upgrade`
- `admin db check-schema`

## Workflow And Node Read Surface

- `workflow start`
- `workflow current`
- `node show`
- `node blockers`

## Session Surface

- `session bind`
- `session show-current`
- `session recover`
- `session provider-resume`

## Documentation Surface

- `docs list`
- `docs show`

## Source Of Truth

For canonical verification commands, use `notes/catalogs/checklists/verification_command_catalog.md`.
For user-facing workflow guidance, use the docs under `docs/user/`, `docs/operator/`, and `docs/runbooks/`.
