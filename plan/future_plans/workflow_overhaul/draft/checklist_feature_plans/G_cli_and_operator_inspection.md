# Slice G: CLI And Operator Inspection

## Goal

Expose checklist state, active item, blockers, and prior results through operator surfaces.

## Main Work

- add checklist inspection reads
- show active item
- show blocker details and unblock conditions
- show `not_applicable` reasons and result history

## Systems

- Database: partial
- CLI: primary
- Daemon: primary
- YAML: not_applicable
- Prompts: partial
- Website UI: partial

## Main Risks

- checklist runtime existing without adequate inspectability
