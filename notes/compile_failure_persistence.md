# Compile Failure Persistence

## Purpose

This document defines how workflow-compilation failures should be recorded and exposed.

The design already assumes that node execution depends on successful compilation of:

- source YAML
- overrides
- policies
- hooks
- resolved task/subtask structures

But until now, compilation failure has mostly existed as an implied setup error rather than a first-class durable event with auditability and operator visibility.

This note closes that gap.

Related documents:

- `notes/yaml_schemas_spec_v2.md`
- `notes/override_conflict_semantics.md`
- `notes/database_schema_spec_v2.md`
- `notes/cross_spec_gap_matrix.md`

---

## Core Rule

Compilation failure is operationally important state and should be durably recorded.

Reason:

- it blocks node readiness
- it may indicate broken specs or overrides
- it may require operator or user intervention
- it should be inspectable later for debugging and auditability

Compilation failure should not live only in logs or transient terminal output.

---

## What Counts As A Compilation Failure

A compilation failure is any failure that prevents a valid immutable workflow snapshot from being produced for a node version.

This includes at least:

- missing required source definitions
- ambiguous duplicate definitions
- override target resolution failure
- override merge conflict
- schema validation failure
- hook expansion failure
- invalid compiled task ordering
- invalid compiled subtask dependency graph
- invalid policy resolution affecting workflow structure

---

## Compilation Stages

The system should conceptually treat compilation as a sequence of stages.

Recommended stages:

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

A failure should be associated with the stage where it occurred.

---

## Failure Classification

Recommended compilation failure classes:

- `missing_source`
- `duplicate_source_ambiguity`
- `override_missing_target`
- `override_merge_conflict`
- `schema_validation_failure`
- `policy_resolution_failure`
- `hook_expansion_failure`
- `compiled_workflow_structure_failure`
- `compiled_dependency_graph_failure`
- `workflow_persistence_failure`
- `unknown_compile_failure`

These classes do not have to be the final literal enum values, but the model should support categories like them.

---

## Minimum Durable Failure Data

When compilation fails, the system should preserve at least:

- node version ID
- logical node ID if useful
- compile stage
- failure class
- summary message
- detailed error payload
- source document set involved
- relevant target family/ID if the failure is override-related
- timestamp

If available, also preserve:

- schema family involved
- hook ID involved
- policy ID involved
- stack trace or internal diagnostic payload

---

## Recommended Persistence Model

The cleanest design is to add a dedicated compile-failure history structure.

Recommended table:

- `compile_failures`

Possible fields:

- `id`
- `node_version_id`
- `failure_stage`
- `failure_class`
- `summary`
- `details_json`
- `source_hash`
- `target_family`
- `target_id`
- `hook_id`
- `policy_id`
- `created_at`

This allows:

- repeated compile attempts
- compile failure history
- CLI visibility
- later analysis of broken override or schema patterns

---

## Alternative Minimal Model

If a dedicated table is too heavy for the first implementation, the minimum acceptable fallback would be:

- node lifecycle state indicating compilation failure
- structured summary row
- structured diagnostic payload stored somewhere durable

This is weaker than a dedicated table and should be treated as a temporary simplification.

Recommended default direction:

- use a dedicated compile-failure table
- pair it with explicit `COMPILE_FAILED` lifecycle visibility in current-state surfaces

---

## Lifecycle Implications

When compilation fails:

1. node version should not transition to `READY`
2. node version should remain in a failed compile state or a paused draft-like state
3. no node run should be admitted against that failed compilation
4. the operator should be able to inspect the failure

Possible lifecycle approaches:

### Option A: reuse `DRAFT` plus compile-failure summary

Pros:

- fewer states

Cons:

- poor operational clarity

### Option B: add explicit compile-failure state

Possible value:

- `COMPILE_FAILED`

Recommended direction:

- strongly consider explicit compile-failure visibility, even if represented through a related failure record plus existing node status model

---

## Reattempt Behavior

Compilation failure should support reattempt after fixes.

The system should allow:

1. inspect failure
2. update source YAML or overrides
3. re-run compilation
4. either:
   - produce a valid compiled workflow
   - produce a new compile failure record

The history of failed compile attempts should remain visible.

---

## Interaction With Overrides

Override-related failures should be especially diagnosable.

For override failures, preserve:

- target family
- target ID
- merge mode
- conflicting field if known
- reason for rejection

This is necessary because override failures are often fixable only if the operator can see what merge assumption was invalid.

---

## Interaction With Hooks

Hook expansion failures should preserve:

- hook ID
- lifecycle insertion point
- node kind or task context
- reason the hook could not be expanded or validated

Hook failures should not disappear into generic compile errors.

---

## Interaction With CLI

The CLI should expose compile failures directly.

Likely useful commands:

- `ai-tool workflow compile-status --node <id>`
- `ai-tool workflow compile-failures --node <id>`
- `ai-tool workflow compile-check --node <id>`

If names differ, these capabilities should still exist.

The operator should be able to answer:

- did compilation fail
- at what stage
- why
- against which inputs

---

## Interaction With Auditability

Auditability requires the system to explain why a node never became runnable.

That means compile-failure persistence is important for:

- debugging
- spec review
- later incident analysis
- comparing failed and successful source configurations

Without durable compile-failure records, failed node versions are too opaque.

---

## Pseudocode

```python
def compile_node_workflow(node_version_id):
    try:
        sources = load_source_documents(node_version_id)
        resolved = resolve_overrides(sources)
        validate_source_yaml(resolved)
        expanded = expand_hooks(resolved)
        workflow = compile_workflow(expanded)
        validate_compiled_graph(workflow)
        persist_compiled_workflow(node_version_id, workflow)
        return "ok"
    except CompileFailure as err:
        record_compile_failure(
            node_version_id=node_version_id,
            stage=err.stage,
            failure_class=err.failure_class,
            details=err.details,
        )
        mark_node_compile_failed(node_version_id)
        return "failed"
```

The implementation should preserve enough structured detail that the failure is inspectable later.

---

## DB Implications

Recommended addition:

- `compile_failures`

Potential indexes:

- `(node_version_id)`
- `(failure_stage)`
- `(failure_class)`
- `(created_at)`

Potential future view:

- `latest_compile_failures`

Purpose:

- expose the most recent compile failure per node version

---

## Recommended Failure Payload Structure

The `details_json` or equivalent should be able to hold:

- stage-specific context
- source document IDs or paths
- schema error lists
- override target data
- hook insertion context
- graph validation errors

This should be structured enough for CLI display and later analysis, not just a blob of raw text.

---

## Recommended Default Policy

For the first serious implementation:

1. add dedicated compile failure persistence
2. classify failures by stage and class
3. block node readiness until compile succeeds
4. expose compile failure status through CLI

This is much safer than treating compilation as an untracked precondition.

---

## Open Decisions Still Remaining

### D01. Dedicated lifecycle state vs failure table only

Recommended direction:

- likely both, or at least a clearly queryable node status plus failure table

### D02. Whether failed compile attempts are attached to version or attempt number

Recommended direction:

- version is sufficient initially
- add compile-attempt numbering later if repeated failures become important operationally

### D03. Whether successful compile events should also be recorded

Recommended direction:

- maybe, but compile failures are the minimum missing piece

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/database_schema_spec_v2.md`
2. `notes/node_lifecycle_spec_v2.md`
3. `notes/cli_surface_spec_v2.md`
4. `notes/cross_spec_gap_matrix.md`

Then reduce the severity of the compile-failure gap.

---

## Exit Criteria

This note is complete enough when:

- compile failure classes are explicit
- compile stages are explicit
- minimum durable failure data is explicit
- DB/CLI/lifecycle implications are identified

At that point, compilation failure is no longer an untracked setup error.
