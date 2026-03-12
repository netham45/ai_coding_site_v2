# Slice C: Durable Checklist Persistence

## Goal

Persist checklist instances, item states, blockers, and results durably.

## Main Work

- add durable checklist storage
- persist active item and item history
- persist blockers and unblock conditions
- persist `not_applicable` decisions

## Systems

- Database: primary
- CLI: partial
- Daemon: primary
- YAML: partial
- Prompts: not_applicable
- Website UI: partial

## Main Risks

- checklist truth living only in prompt text
- item/result history becoming non-reconstructible
