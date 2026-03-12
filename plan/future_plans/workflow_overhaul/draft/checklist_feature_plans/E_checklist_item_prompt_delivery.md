# Slice E: Checklist Item Prompt Delivery

## Goal

Deliver a bounded prompt for one active checklist item with explicit `When To Use This` guidance and a strict terminal return contract.

## Main Work

- add checklist-item prompt assets
- render item-specific allowed options
- inject overarching task and active item context
- enforce structured terminal result shape

## Systems

- Database: not_applicable
- CLI: partial
- Daemon: primary
- YAML: partial
- Prompts: primary
- Website UI: not_applicable

## Main Risks

- prompt drift from daemon legality
- worker treating one item as the whole task
