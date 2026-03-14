# Setup 00: Bundle Normalization And Contract Freeze

## Goal

Turn the current workflow-overhaul bundle into a stable authoritative planning surface before code changes begin.

## Main Work

- normalize the bundle into setup plans, feature plans, and supporting assets
- freeze vocabulary for profiles, layouts, briefs, blocked mutations, task-sequence templates, generated tasks, and one-off authored decomposition
- identify which current notes remain draft-only and which must become authoritative first

## Main Outputs

- stable planning taxonomy
- sequence note
- draft-to-authoritative promotion map

## Implementation Subtasks

- inventory every note and asset family in `workflow_overhaul/` and assign it to setup, feature, asset, or proving support
- freeze the core vocabulary for profiles, layouts, briefs, blocked mutations, task-sequence templates, template provenance, generated-task lineage, and one-off authored decomposition
- define the authoritative-vs-draft promotion rule for the bundle so later plans know which notes must be upgraded first
- write the bundle index and sequencing note that downstream setup/feature plans will reference

## Main Dependencies

- none

## Flows Touched

- touches all workflow-overhaul-affected flows indirectly by freezing contract language first

## Relevant Current Code

- `tests/unit/test_task_plan_docs.py`
- `tests/unit/test_document_schema_docs.py`
- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`

## Current Gaps

- the draft workflow-overhaul family itself is not yet an authoritative document family with its own consistency tests
- current code has no workflow-profile or template-aware compile contract to freeze against, so this setup slice must normalize notes before code can follow
