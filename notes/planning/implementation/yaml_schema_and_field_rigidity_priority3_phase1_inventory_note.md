# YAML Schema And Field Rigidity Priority 3 Phase 1 Inventory Note

## Purpose

This note records the Phase 1 inventory for `plan/tasks/2026-03-11_yaml_schema_and_field_rigidity_priority3.md`.

The goal of this phase is to confirm the actual authored-library surface and current proving layers for the deferred Priority 3 YAML families:

- `hook_definition`
- `runtime_policy_definition`
- `testing_definition`
- `docs_definition`

## Authored Family Inventory

### Hook definitions

Current built-in authored inventory under `hooks/`:

- `after_merge_children_default.yaml`
- `after_node_complete_build_docs.yaml`
- `after_node_complete_default.yaml`
- `after_node_complete_update_provenance.yaml`
- `after_review_default.yaml`
- `after_subtask_default_summary.yaml`
- `after_testing_default.yaml`
- `after_upstream_rectify_default.yaml`
- `after_validation_default.yaml`
- `before_merge_children_default.yaml`
- `before_node_complete_default.yaml`
- `before_review_default.yaml`
- `before_testing_default.yaml`
- `before_upstream_rectify_default.yaml`
- `before_validation_default.yaml`
- `default_hooks.yaml`
- `on_merge_conflict_default.yaml`
- `on_node_created_default.yaml`

### Runtime policy definitions

Current built-in authored inventory under `policies/`:

- `default_failure_policy.yaml`
- `default_merge_policy.yaml`
- `default_node_policy.yaml`
- `default_review_policy.yaml`
- `default_runtime_policy.yaml`
- `default_testing_policy.yaml`

Only `default_runtime_policy.yaml` is a `runtime_policy_definition`. The other built-ins in that folder are adjacent policy families and are out of scope for this task.

### Testing definitions

Current built-in authored inventory under `testing/`:

- `default_integration_test_gate.yaml`
- `default_smoke_test_gate.yaml`
- `default_unit_test_gate.yaml`
- `project_command_suite.yaml`
- `pytest_suite.yaml`
- `test_failure_summary.yaml`
- `test_retry_policy.yaml`

### Docs definitions

Current built-in authored inventory under `docs/`:

- `build_docs.yaml`
- `build_local_node_docs.yaml`
- `build_merged_tree_docs.yaml`
- `default_doc_views.yaml`
- `entity_history_view.yaml`
- `rationale_merge_rules.yaml`
- `static_analysis_scope.yaml`

## Current Proving Layers

### Shared proving already present

These families are not untested. They already participate in several proving layers:

- generic YAML schema validation in `tests/unit/test_yaml_schemas.py`
- grouped library checks:
  - `tests/unit/test_operational_library.py`
  - `tests/unit/test_quality_library.py`
- runtime/compile/integration surfaces:
  - hook/runtime-policy compile and effective-policy paths
  - testing runtime and result-routing paths
  - docs build/list/show paths
- prompt-binding proof where the family carries prompt refs

### What those existing layers already prove

- the families are recognized and validate at the schema layer
- required built-in library anchor files exist
- prompt-bearing references are not obviously broken
- the real daemon/CLI/runtime surfaces still function with the authored built-ins

### What is still thin

The still-thin layer is authored-family rigidity.

The current repo does not yet have dedicated family-library tests that iterate each shipped YAML in these families and assert the family-specific invariants directly.

Examples of currently under-expressed invariants:

- hooks:
  - unique ids across authored hook docs
  - non-empty `when`
  - every run step has the required command or prompt for its declared type
  - prompt-bearing run steps keep prompt refs intact across the whole built-in family
- runtime policies:
  - unique ids across authored runtime-policy docs
  - non-empty defaults
  - unique refs per ref bucket
  - every ref resolves to a matching-family built-in asset
- testing definitions:
  - unique ids across authored testing docs
  - non-empty scope
  - non-empty command strings and working directories across the entire family
  - declared `on_result` actions remain non-empty in authored docs
- docs definitions:
  - unique ids across authored docs docs
  - non-empty scope
  - non-empty outputs
  - non-empty output paths/views across the entire family

## Family Classification Outcome

### `hook_definition`

Classification:

- still a real Priority 3 family-library gap

Reason:

- compile/runtime proof is meaningful
- operational-library proof exists
- but the authored hook family still lacks a direct per-family rigidity pass

### `runtime_policy_definition`

Classification:

- still a real Priority 3 family-library gap

Reason:

- effective-policy and compile/runtime proof exists
- operational-library proof exists
- but there is no dedicated authored runtime-policy rigidity test

### `testing_definition`

Classification:

- still a real Priority 3 family-library gap

Reason:

- quality-library and testing-runtime proof are meaningful
- but there is no dedicated authored testing-library rigidity test

### `docs_definition`

Classification:

- still a real Priority 3 family-library gap

Reason:

- quality-library and docs-runtime proof are meaningful
- but there is no dedicated authored docs-library rigidity test

## Phase 1 Result

The inventory confirms that all four deferred families still need the same kind of improvement:

- not a brand-new runtime surface
- not broad new daemon logic
- not one-file-per-asset tests

They need explicit authored-family rigidity tests, plus any narrowly justified schema-negative additions that remain missing.

## Next Step

Phase 2 should add the dedicated family-library tests for these four families and widen `tests/unit/test_yaml_schemas.py` only where a real negative-case gap still exists.
