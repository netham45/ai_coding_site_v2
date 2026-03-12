# Slice I: E2E Coverage

## Goal

Prove checklist execution mode through real runtime narratives.

## Main Work

- prove single active item execution
- prove blocked item persistence and later unblock
- prove `not_applicable` handling
- prove recovery and inspection behavior

## Systems

- Database: primary
- CLI: primary
- Daemon: primary
- YAML: partial
- Prompts: partial
- Website UI: partial

## Main Risks

- stopping at schema validation or prompt existence
- using synthetic item advancement instead of real runtime progression
