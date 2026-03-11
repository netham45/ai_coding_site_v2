# YAML Schema And Field Rigidity Phase 1 Inventory Note

## Purpose

This note records the Phase 1 inventory for `plan/tasks/2026-03-11_yaml_schema_and_field_rigidity_investigation.md`.

The goal of this phase is to identify the active YAML families, the validator model for each family, and the current proving layer already present in code and tests before any new rigidity-test implementation begins.

## Sources Reviewed

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/quality_library.py`
- `src/aicoding/operational_library.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/`
- `src/aicoding/resources/yaml/project/project-policies/`
- `tests/unit/test_yaml_schemas.py`
- `tests/unit/test_structural_library.py`
- `tests/unit/test_quality_library.py`
- `tests/unit/test_operational_library.py`
- `tests/unit/test_subtask_library.py`
- `tests/integration/test_default_yaml_library.py`
- `tests/integration/test_yaml_validation.py`
- `tests/unit/test_workflows.py`
- `tests/unit/test_prompt_pack.py`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`

## Current Active YAML Families

All active YAML families currently route through explicit validator models in `src/aicoding/yaml_schemas.py`.

### Built-in system families

- `node_definition`
  - directory: `nodes/`
  - current file count: 4
  - validator: `NodeDefinitionDocument`
- `task_definition`
  - directory: `tasks/`
  - current file count: 23
  - validator: `TaskDefinitionDocument`
- `subtask_definition`
  - directory: `subtasks/`
  - current file count: 23
  - validator: `SubtaskDefinitionDocument`
- `layout_definition`
  - directory: `layouts/`
  - current file count: 6
  - validator: `LayoutDefinitionDocument`
- `validation_definition`
  - directory: `validations/`
  - current file count: 14
  - validator: `ValidationDefinitionDocument`
- `review_definition`
  - directory: `reviews/`
  - current file count: 7
  - validator: `ReviewDefinitionDocument`
- `testing_definition`
  - directory: `testing/`
  - current file count: 7
  - validator: `TestingDefinitionDocument`
- `docs_definition`
  - directory: `docs/`
  - current file count: 7
  - validator: `DocsDefinitionDocument`
- `hook_definition`
  - directory: `hooks/`
  - current file count: 18
  - validator: `HookDefinitionDocument`
- `rectification_definition`
  - directory: `rectification/`
  - current file count: 8
  - validator: `RectificationDefinitionDocument`
- `runtime_definition`
  - directory: `runtime/`
  - current file count: 6
  - validator: `RuntimeDefinitionDocument`
- `runtime_policy_definition`
  - directory: `policies/`
  - current file count: 6
  - validator: `RuntimePolicyDefinitionDocument`
- `environment_policy_definition`
  - directory: `environments/`
  - current file count: 2
  - validator: `EnvironmentPolicyDefinitionDocument`
- `prompt_reference_definition`
  - directory: `prompts/`
  - current file count: 1
  - validator: `PromptReferenceDefinitionDocument`

### Project and override families

- `project_policy_definition`
  - directory: `src/aicoding/resources/yaml/project/project-policies/`
  - current file count: 1
  - validator: `ProjectPolicyDefinitionDocument`
- `override_definition`
  - directory: project-local override roots
  - current packaged file count: 0
  - validator: `OverrideDefinitionDocument`
  - proving today is fixture-based rather than packaged-library-based

## Current Proving Groups

The proving surface is already split into four distinct layers.

### 1. Generic schema validation

Primary tests:

- `tests/unit/test_yaml_schemas.py`
- `tests/integration/test_yaml_validation.py`

What this layer proves:

- every active YAML family is registered in `schema_family_descriptors()`
- `validate_yaml_document(...)` can identify and validate built-in, project-policy, and override documents
- the daemon and CLI expose YAML schema-family listing and single-document validation
- validation reports persist durably through `persist_yaml_validation_report(...)`

What this layer does not prove:

- every built-in file in every directory has family-specific field rigidity tests
- family-specific cross-file reference integrity
- compile/runtime behavior for families that affect workflow assembly or runtime policy

### 2. Family-library integrity tests

Primary tests:

- `tests/unit/test_structural_library.py`
- `tests/unit/test_quality_library.py`
- `tests/unit/test_operational_library.py`
- `tests/unit/test_subtask_library.py`

What this layer proves:

- required built-in files exist by family group
- optional built-ins are surfaced explicitly
- selected cross-file references are checked inside each library inspector
- some family-specific invariants already exist, such as:
  - structural node task references and prompt references
  - quality gate ordering and review/testing/docs binding consistency
  - operational prompt-binding and required hook/runtime/policy presence
  - subtask prompt binding, destructive-command guardrails, and synthetic startability

What this layer does not prove:

- rigid negative tests for every meaningful field in every family
- equivalent field-level checks for families that do not have a dedicated library inspector

### 3. Workflow compile and runtime integration

Primary tests:

- `tests/integration/test_default_yaml_library.py`
- `tests/unit/test_workflows.py`
- selected runtime tests that compile real workflows before validation, review, testing, docs, child-session, or materialization work

What this layer proves:

- authored built-in node kinds compile through the real compile path
- invalid structural, quality, and operational library payloads can fail compilation with typed failure classes
- layout YAML participates in child materialization and register-layout flows
- testing, docs, reviews, hooks, runtime policy, and environment policy families influence compiled workflow state

What this layer does not prove:

- every YAML family has a dedicated integration failure case
- every individual field is defended at the family boundary rather than indirectly through successful compile

### 4. Prompt-reference and prompt-binding integrity

Primary tests:

- `tests/unit/test_prompt_pack.py`
- `tests/unit/test_subtask_library.py`
- `tests/unit/test_operational_library.py`

What this layer proves:

- YAML prompt-bearing documents resolve to real prompt assets
- the packaged prompt-reference YAML is valid and internally consistent
- unbound prompt files are now rejected by a bounded test

This matters to the YAML investigation because prompt-reference YAML is one of the active YAML families and several other YAML families are only operationally correct when their prompt paths resolve.

## Family Classification Snapshot

This is the current Phase 1 classification of the proving layer by family.

- `node_definition`
  - current layer: schema validation, structural-library integrity, compile/runtime integration
  - current rigidity strength: medium
- `task_definition`
  - current layer: schema validation, structural-library integrity, quality-library integrity, compile/runtime integration
  - current rigidity strength: medium
- `subtask_definition`
  - current layer: schema validation, subtask-library integrity, synthetic compile/start integration
  - current rigidity strength: medium-high
- `layout_definition`
  - current layer: schema validation, structural-library integrity, materialization/runtime integration
  - current rigidity strength: medium
- `validation_definition`
  - current layer: schema validation, quality-library integrity
  - current rigidity strength: low-medium
- `review_definition`
  - current layer: schema validation, quality-library integrity, prompt-asset validation
  - current rigidity strength: medium
- `testing_definition`
  - current layer: schema validation, quality-library integrity, selected runtime integration
  - current rigidity strength: medium
- `docs_definition`
  - current layer: schema validation, quality-library integrity, selected runtime integration
  - current rigidity strength: medium
- `hook_definition`
  - current layer: schema validation, operational-library integrity, compile/runtime integration
  - current rigidity strength: medium
- `rectification_definition`
  - current layer: schema validation only plus one higher-order negative-field test
  - current rigidity strength: low
- `runtime_definition`
  - current layer: schema validation, operational-library integrity
  - current rigidity strength: low-medium
- `runtime_policy_definition`
  - current layer: schema validation, operational-library integrity, selected compile/runtime integration
  - current rigidity strength: medium
- `environment_policy_definition`
  - current layer: schema validation, selected compile/runtime integration
  - current rigidity strength: low-medium
- `prompt_reference_definition`
  - current layer: schema validation, prompt-binding integrity, operational/quality reference checks
  - current rigidity strength: high
- `project_policy_definition`
  - current layer: schema validation, selected compile/runtime integration
  - current rigidity strength: low-medium
- `override_definition`
  - current layer: schema validation, selected compile/runtime integration
  - current rigidity strength: low-medium

## Phase 1 Findings

### Main finding 1

The repository does not have a single YAML proving surface. It has:

- generic schema validation
- library-family integrity checks
- compile/runtime integration checks
- prompt-binding checks for prompt-bearing YAML

That means later work should not treat "schema-valid" as equivalent to "rigidly tested."

### Main finding 2

Structural, quality, and operational YAML are already treated as grouped library contracts, not just individual files. The future rigidity plan should preserve that grouping instead of scattering one-off file tests everywhere.

### Main finding 3

The weakest currently defended families are:

- `rectification_definition`
- `runtime_definition`
- `environment_policy_definition`
- `project_policy_definition`
- `override_definition`
- parts of `validation_definition`

These families have explicit schema models, but much thinner family-specific field coverage than the structural, subtask, and prompt-reference surfaces.

### Main finding 4

Some family coverage is indirect. For example:

- environment-policy behavior is partly defended through workflow compilation
- override behavior is partly defended through compile and materialization flows
- docs/testing/review families are partly defended through grouped quality-library invariants rather than direct per-field rigidity tests

Phase 2 needs to separate intentional grouped coverage from actual field-rigidity gaps.

## Next Step

Phase 2 should classify the real gaps:

- families that are only schema-covered
- families that have grouped-library coverage but weak field assertions
- families that need daemon/CLI integration proof because they affect compile-time or runtime decisions
