# Feature 08: Checklist Schema Family

## Goal

Adopt checklist schema, template, and instance families as real validated assets.

## Main Work

- add checklist schema models
- validate item status vocabulary, blocker shape, and `not_applicable`
- constrain item-kind payloads

## Implementation Subtasks

- add real schema models for checklist schema definitions, checklist templates, and checklist instances
- freeze the allowed item-status vocabulary including `not_applicable`
- define and validate the blocker schema including `unblocks_when`
- constrain per-item-kind payload shapes so checklist instances cannot invent arbitrary structure

## Main Dependencies

- Setup 00
- Setup 01

## Flows Touched

- future checklist flows
- `02_compile_or_recompile_workflow_flow`

## Relevant Current Code

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/db/models.py`

## Current Gaps

- there is no checklist schema, template, or instance family in current YAML validation code
- there is no current durable model for checklist vocabulary, blockers, or `not_applicable`
