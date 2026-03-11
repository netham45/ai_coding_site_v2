# YAML Schema And Field Rigidity Phase 3 Test Strategy Note

## Purpose

This note freezes the recommended test structure for the YAML rigidity follow-on work governed by `plan/tasks/2026-03-11_yaml_schema_and_field_rigidity_investigation.md`.

The goal is to add stronger YAML rigidity proof without collapsing into low-value duplication or violating the code-vs-YAML boundary.

## Strategy Rules

### Rule 1: Expand by family bucket, not by file count

The implementation should add rigidity tests in grouped batches that match the Phase 2 taxonomy:

- Priority 1 weak families
- Priority 2 compile/runtime-sensitive but field-thin families
- Priority 3 later enrichment families

### Rule 2: Prefer family-level authored-library assertions over one-file-per-test sprawl

Where a family has multiple built-in authored documents, the new tests should:

- iterate the family directory
- validate expected required fields and invariants by document
- report the failing relative path explicitly

Do not write one bespoke unit test for every YAML file unless one document carries a unique invariant that cannot be expressed generically.

### Rule 3: Keep schema-negative, library-level, and integration-level proof separate

The new proving layer should use three distinct forms:

- schema-negative tests
  - prove validator models reject illegal field combinations
- family-library rigidity tests
  - prove authored built-in documents meet the intended invariant set
- integration tests
  - prove YAML families that affect compile/runtime behavior still surface failures correctly through daemon or CLI boundaries

### Rule 4: Do not re-prove code-owned orchestration decisions in YAML tests

YAML rigidity tests should focus on:

- declarative shape
- allowed references
- authored library integrity
- family-specific field invariants
- compile-time contract failures where YAML is the trigger

They should not attempt to own:

- session scheduling semantics
- live daemon coordination
- git conflict resolution behavior
- recovery loop algorithms

## Recommended Test Structure By Family Bucket

### Priority 1 families

#### `rectification_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add negative cases for:
    - empty `trigger`
    - empty `entry_task`
    - duplicate `subtasks`
    - empty `subtasks`
- add new family-library test file or extend an existing YAML family test
  - iterate `rectification/*.yaml`
  - assert:
    - every file validates
    - `entry_task` points at an existing built-in task
    - every referenced subtask id points at an existing built-in subtask asset or canonical subtask catalog id
    - no duplicate subtasks exist in authored docs
- add one compile-adjacent integration proof only if a real daemon or compile path already consumes rectification definitions directly in this scope

Why this structure:

- the family is currently the weakest true gap
- most missing proof is declarative and cross-reference oriented, not runtime-algorithmic

#### `environment_policy_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add negative cases for:
    - unsupported `isolation_mode`
    - missing `runtime_profile` for `custom_profile`
    - illegal `runtime_profile` when not in `custom_profile`
- add new family-library assertions
  - iterate `environments/*.yaml`
  - assert:
    - every file validates
    - ids are unique
    - `custom_profile` declarations use non-empty `runtime_profile`
    - built-in profiles referenced by runtime-sensitive task/subtask surfaces are actually present
- retain and possibly widen compile integration
  - keep the existing compile failure for undeclared environment profile
  - add one success-path integration if missing for declared environment profile propagation

Why this structure:

- the family is small, so field-rigidity can be explicit and cheap
- integration proof matters because the family affects runtime isolation requests

#### `validation_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add targeted negative cases for the less-exercised `ValidationCheckDefinition` variants, not only current sample failures
- add a new built-in validation-library rigidity test
  - iterate `validations/*.yaml`
  - assert:
    - every file validates
    - ids are unique
    - each built-in check type expected by the authored library appears exactly where intended
    - check-specific required fields are present in the authored built-ins
- preserve grouped quality-library checks
  - do not replace them
  - use them as the cross-file binding surface
- integration additions only where validation YAML actually routes through daemon compile/validation surfaces

Why this structure:

- the family has many built-in documents and many check variants
- current proof is strong at the model level but thin at the authored-library level

### Priority 2 families

#### `runtime_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add negative cases for:
    - empty command entry
    - duplicate actions
    - missing threshold payload
- add a dedicated built-in runtime-family rigidity test
  - iterate `runtime/*.yaml`
  - assert:
    - validation passes
    - ids are unique
    - every action ref resolves to a real subtask file
    - thresholds contain the expected keys for the authored built-ins where those keys are part of the intended contract
- keep operational-library tests as the grouped cross-family surface

#### `project_policy_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add negative cases beyond invalid node kind, especially around malformed refs and invalid prompt-pack assumptions if supported by the model
- add a project-policy family test
  - validate each packaged project policy
  - assert all refs normalize to existing built-in assets
  - assert enabled node kinds resolve through the hierarchy registry
- retain policy-resolution and flow-contract tests as integration proof

#### `override_definition`

Recommended proving shape:

- extend `tests/unit/test_yaml_schemas.py`
  - add negative cases for:
    - unsupported target family
    - unsupported merge mode
    - empty `value`
- add a new override-rigidity family test using fixture-authored overrides
  - assert merge modes and target families are accepted/rejected as intended
  - assert only supported top-level family fields are used for the scoped fixtures
- keep compile/runtime integration through workflow compilation and flow-contract tests

### Priority 3 families

#### `hook_definition`, `runtime_policy_definition`, `testing_definition`, `docs_definition`

Recommended proving shape:

- keep existing grouped-library and compile/runtime proof
- add richer family-level rigidity only after Priority 1 and 2 families land
- prefer grouped per-family loops over bespoke document tests

## Recommended Test File Layout

The current proving surface can absorb the next work without a broad test-file explosion.

Recommended placements:

- `tests/unit/test_yaml_schemas.py`
  - keep model-level negative validation and family-descriptor coverage
- new or expanded family-library files:
  - `tests/unit/test_rectification_library.py`
  - `tests/unit/test_environment_library.py`
  - `tests/unit/test_validation_library.py`
  - `tests/unit/test_runtime_library.py`
  - `tests/unit/test_project_policy_library.py`
  - `tests/unit/test_override_rigidity.py`
- existing grouped-library files remain:
  - `tests/unit/test_structural_library.py`
  - `tests/unit/test_quality_library.py`
  - `tests/unit/test_operational_library.py`
  - `tests/unit/test_subtask_library.py`
- existing integration surfaces remain the first place for daemon/CLI compile/validation proof:
  - `tests/integration/test_yaml_validation.py`
  - `tests/integration/test_default_yaml_library.py`
  - `tests/integration/test_flow_yaml_contract_suite.py`
  - selected workflow compile tests in `tests/unit/test_workflows.py`

## Performance Guidance

The new rigidity layer should avoid repeated expensive full-library scans in many tests.

Preferred pattern:

- one family loop per test
- explicit relative-path assertions in failure messages
- reuse `load_resource_catalog()` once per test where practical

Do not add:

- repeated whole-library validation inside every family test
- daemon or CLI integration invocations for families that are fully provable at the unit/library layer

## Observability And Auditability Guidance

The rigidity batch should preserve operator-inspectable surfaces by continuing to test:

- `validate_yaml_document(...)`
- persisted validation reports
- daemon `/api/yaml/validate`
- CLI `yaml validate`

Family-level rigidity tests are additive. They should not replace the generic inspection surfaces that operators use.

## Phase 3 Output

The follow-on implementation plan should be phased as:

1. Priority 1 family rigidity
2. Priority 2 family rigidity
3. integration supplementation only where still missing
4. notes/checklist refresh and status hardening
