# Module: `compile_workflow(...)`

## Purpose

Produce an immutable compiled workflow snapshot for a node version from YAML sources, overrides, hooks, and policy inputs.

This module is the boundary between mutable design-time definitions and runnable execution artifacts.

---

## Source notes

Primary:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/contracts/persistence/compile_failure_persistence.md`

Supporting:

- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

---

## Inputs

- `node_version_id`
- `logical_node_id`
- `node_kind`
- `node_tier`
- built-in YAML source set applicable to the node
- project-local extension YAML source set applicable to the node
- project-local override YAML source set applicable to the node
- project policy documents applicable to the node

Optional inputs:

- explicit operator compile request
- compile target context:
  - authoritative
  - candidate
  - rebuild candidate
- prior compile failure records
- default built-in library version/hash

---

## Required state

- the node version exists and is the intended compile target
- the node version is not cut over to an incompatible superseding version during compilation
- applicable source families are discoverable
- source lineage can be persisted
- compile-failure history is writable
- no execution run is admitted from this node version until compilation succeeds

---

## Outputs

On success:

- compiled workflow snapshot
- compiled workflow hash
- compiled tasks and compiled subtasks with durable IDs
- source lineage records
- resolved YAML snapshot
- compile success event or equivalent durable record
- node version marked runnable or ready for admission

On failure:

- structured compile failure record
- node version left non-runnable
- no compiled workflow made authoritative

---

## Durable writes

Success path should write at least:

- source lineage records for all workflow-affecting documents
- resolved merged YAML snapshot or equivalent normalized representation
- compiled workflow row/header
- compiled task rows
- compiled subtask rows
- hook insertion lineage metadata where applicable
- workflow hash and compile timestamp
- frozen compile context for the targeted node version
- node-version readiness or compile-success state transition

Failure path should write at least:

- compile failure record with:
  - `node_version_id`
  - `failure_stage`
  - `failure_class`
  - `summary`
  - `details_json`
  - relevant source lineage or source hash
  - target family and target ID where applicable
  - hook ID or policy ID where applicable
- node version compile-failed or equivalent blocked state

---

## Stage model

Compilation is treated as these ordered stages:

1. source discovery
2. source loading
3. extension resolution
4. override resolution
5. schema validation
6. policy resolution
7. hook expansion
8. workflow compilation
9. compiled graph validation
10. workflow persistence

Every failure should be associated with one of these stages.

---

## Happy path

```text
function compile_workflow(node_version_id):
  assert node_version_exists(node_version_id)
  assert node_version_is_compile_target(node_version_id)

  context = load_node_compile_context(node_version_id)

  try:
    mark_compile_attempt_started(node_version_id)

    stage = "source_discovery"
    source_refs = discover_applicable_sources(context)
    assert_required_source_families_present(source_refs)

    stage = "source_loading"
    source_docs = load_source_documents(source_refs)
    assert_source_docs_are_hashable_and_traceable(source_docs)

    stage = "extension_resolution"
    layered_docs = partition_sources_by_precedence(source_docs)
    assert_duplicate_extension_ambiguities_are_bounded(layered_docs)

    stage = "override_resolution"
    resolved_docs = resolve_overrides(
      built_in_defs = layered_docs.built_ins,
      extension_defs = layered_docs.extensions,
      override_defs = layered_docs.overrides
    )

    stage = "schema_validation"
    validate_source_yaml(resolved_docs)

    stage = "policy_resolution"
    policy_context = resolve_project_policies(resolved_docs, context)
    assert_policy_outcomes_do_not_violate_compile_boundary(policy_context)

    stage = "hook_expansion"
    expanded_docs = expand_hooks(
      resolved_docs = resolved_docs,
      policy_context = policy_context,
      node_context = context
    )

    stage = "workflow_compilation"
    compiled_workflow = compile_resolved_definitions_into_immutable_workflow(
      expanded_docs,
      node_context = context
    )
    assign_durable_compiled_ids(compiled_workflow)
    freeze_prompts_commands_dependencies(compiled_workflow)

    stage = "compiled_graph_validation"
    validate_compiled_workflow_structure(compiled_workflow)
    validate_compiled_dependency_graph(compiled_workflow)
    validate_quality_gate_order(compiled_workflow)

    stage = "workflow_persistence"
    begin_transaction()
    persist_source_lineage(node_version_id, source_docs, resolved_docs, expanded_docs)
    persist_compiled_workflow(node_version_id, compiled_workflow)
    clear_active_compile_failure_block(node_version_id)
    mark_node_version_ready_for_run(node_version_id, compiled_workflow.workflow_hash)
    commit_transaction()

    register_compile_success(node_version_id, compiled_workflow.workflow_hash)
    return CompileResult(status = "ok", workflow_id = compiled_workflow.id)

  except CompileFailure as err:
    rollback_transaction_if_open()
    record_compile_failure(
      node_version_id = node_version_id,
      failure_stage = stage,
      failure_class = err.failure_class,
      summary = err.summary,
      details_json = err.details,
      source_refs = best_effort_source_refs(),
      target_family = err.target_family,
      target_id = err.target_id,
      hook_id = err.hook_id,
      policy_id = err.policy_id
    )
    mark_node_version_compile_failed(node_version_id, stage, err.failure_class)
    return CompileResult(status = "failed", failure_stage = stage)

  except Exception as err:
    rollback_transaction_if_open()
    record_compile_failure(
      node_version_id = node_version_id,
      failure_stage = stage,
      failure_class = "unknown_compile_failure",
      summary = summarize_unexpected_compile_error(err),
      details_json = serialize_unexpected_error(err),
      source_refs = best_effort_source_refs()
    )
    mark_node_version_compile_failed(
      node_version_id,
      stage,
      "unknown_compile_failure"
    )
    return CompileResult(status = "failed", failure_stage = stage)
```

---

## Failure paths

### Missing source definitions

- fail at `source_discovery`
- write `missing_source`
- do not create a partial workflow

### Duplicate definition ambiguity

- fail during `extension_resolution`
- write `duplicate_source_ambiguity`
- preserve the ambiguous source set in diagnostics

### Override failure

- fail during `override_resolution`
- classify as `override_missing_target` or `override_merge_conflict`
- preserve target family, target ID, and merge mode when available

### YAML/schema failure

- fail during `schema_validation`
- preserve the schema family and offending document

### Policy-resolution failure

- fail during `policy_resolution`
- preserve the policy ID and rejected effect

### Hook-expansion failure

- fail during `hook_expansion`
- preserve hook ID, insertion point, and reason

### Compiled structure or dependency failure

- fail during `compiled_graph_validation`
- preserve the invalid ordering, dependency edge, or duplicate-sensitive pattern

### Persistence failure

- fail during `workflow_persistence`
- record `workflow_persistence_failure`
- leave the node version non-runnable

---

## Pause/recovery behavior

This module does not pause for user input as part of normal runtime execution.

Recovery rules:

- a failed compile is recoverable only by changing inputs and recompiling
- later successful compile attempts must not erase compile-failure history
- no node run should bind to a failed or stale compiled workflow snapshot

---

## CLI-visible expectations

Operators and AI clients should be able to ask:

- did compile succeed
- if not, at what stage
- why
- against which source set
- which compiled workflow hash is authoritative now

Minimum corresponding capabilities:

- compile status query
- compile failure history query
- source lineage query
- resolved YAML query
- compiled workflow query

---

## Open questions

- should compile success itself be stored as dedicated history or inferred from the latest authoritative workflow snapshot
- should `COMPILE_FAILED` be a first-class lifecycle state or a derived blocked condition
- what is the exact transaction boundary between resolved YAML persistence and compiled workflow persistence
- should hook expansion preserve pre-expansion intermediate artifacts durably or only in diagnostics

---

## Pseudotests

### `compiles_valid_node_version`

Given:

- required source families exist
- overrides resolve cleanly
- hooks expand deterministically
- compiled graph validates

Expect:

- compiled workflow is persisted
- source lineage is persisted
- node version becomes runnable

### `fails_when_required_source_is_missing`

Given:

- a node kind requires a task definition that does not exist

Expect:

- compile fails at `source_discovery`
- failure class is `missing_source`
- no workflow is persisted

### `fails_when_override_targets_missing_definition`

Given:

- an override references a target family and ID that do not exist

Expect:

- compile fails at `override_resolution`
- failure class is `override_missing_target`
- diagnostics preserve target family and target ID

### `fails_when_hook_breaks_quality_gate_order`

Given:

- a hook inserts testing before review in a context where canonical order forbids it

Expect:

- compile fails during `hook_expansion` or `compiled_graph_validation`
- no invalid workflow becomes authoritative

### `retains_compile_failure_history_across_reattempts`

Given:

- compile attempt one fails
- inputs are fixed
- compile attempt two succeeds

Expect:

- failure history for attempt one remains queryable
- attempt two produces a new authoritative workflow
