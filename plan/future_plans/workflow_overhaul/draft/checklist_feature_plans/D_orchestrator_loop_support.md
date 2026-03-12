# Slice D: Orchestrator Loop Support

## Goal

Run one checklist item at a time and return control to the orchestrator after each terminal item result.

## Main Work

- select next legal item
- prevent multi-item self-advancement
- enforce dependency ordering
- handle blocked, failed, completed, and `not_applicable` item results

## Systems

- Database: partial
- CLI: partial
- Daemon: primary
- YAML: partial
- Prompts: partial
- Website UI: not_applicable

## Main Risks

- checklist loop bypassing workflow authority
- dependency ordering not staying durable after restart
