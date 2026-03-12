# Slice F: Item Completion And Blocker Enforcement

## Goal

Validate checklist item terminal results against structured completion and blocker rules.

## Main Work

- validate `completed` against completion predicates
- validate `blocked` against blocker schema
- validate `not_applicable` against template rules
- expose blocked reasons and unblock conditions

## Systems

- Database: partial
- CLI: partial
- Daemon: primary
- YAML: partial
- Prompts: partial
- Website UI: partial

## Main Risks

- trusting freeform model claims
- `not_applicable` becoming an unstructured skip path
