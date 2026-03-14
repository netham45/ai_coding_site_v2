# Feature 16: Templated Task Generation E2E And Flow Adoption

## Goal

Prove template-driven child generation through real runtime narratives and promote the relevant canonical flows when the behavior becomes operator-relevant.

## Main Work

- add real E2E coverage for template-driven materialization
- prove normal dependency execution across generated children
- prove operator inspection of generated provenance
- promote the new future flows when warranted

## Implementation Subtasks

- implement real E2E coverage for template selection, child generation, and dependency execution
- prove restart and recovery behavior for generated child lineage
- add CLI and website inspection E2E coverage for generated provenance where applicable
- promote future flow drafts into canonical flow and relevant-flow inventory artifacts once runtime behavior is real

## Main Dependencies

- Setup 03
- Features 08 through 14

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `10_regenerate_and_rectify_flow`

## Relevant Current Code

- `tests/e2e/`
- `tests/unit/test_flow_e2e_alignment_docs.py`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- there are no template-driven real E2E routes, browser tests, or canonical flow entries
- the current future-plan inventory still centers a superseded checklist runtime instead of generated-task narratives
