# Slice H: Website UI Support

## Goal

Render checklist state and bounded item actions in the website UI.

## Main Work

- add checklist list/detail views
- show active item and blocker state
- render `not_applicable` reasons
- expose bounded item actions backed by daemon legality

## Systems

- Database: partial
- CLI: not_applicable
- Daemon: primary
- YAML: not_applicable
- Prompts: not_applicable
- Website UI: primary

## Main Risks

- browser state drifting from daemon authority
