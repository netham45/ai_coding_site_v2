# Flow 02: Compile Or Recompile Workflow

## Purpose

Turn source YAML, overrides, hooks, and policy into an immutable compiled workflow snapshot, or record a durable compile failure.

## Covers journeys

- workflow compilation during creation
- recompile after layout, policy, or override changes
- inspect and reject recompile attempts while an authoritative run is still active
- compile-failure inspection and retry

## Entry conditions

- a node version exists
- one or more source documents have been selected or updated

## Task flow

1. load authoritative source documents for the target node version
2. resolve overrides according to merge semantics
3. validate source YAML schemas
4. expand hooks in canonical order
5. validate the resolved workflow
6. compile tasks, subtasks, policies, and hook insertions into immutable runtime artifacts
7. persist workflow hashes and source lineage
8. if compilation fails, persist compile-failure class, evidence, and summary

## Required subtasks

- `load_authoritative_sources`
- `resolve_overrides`
- `validate_source_yaml`
- `expand_hooks`
- `validate_resolved_workflow`
- `compile_workflow_snapshot`
- `persist_compiled_workflow`
- `persist_compile_failure_if_needed`

## Required capabilities

- `ai-tool workflow compile --node <id>`
- `ai-tool yaml validate ...`
- `ai-tool yaml show ...`
- `ai-tool yaml resolved ...`
- `ai-tool hooks list|show ...`
- `ai-tool workflow show ...`
- compile-failure persistence and read surfaces

## Durable outputs

- resolved workflow representation
- compiled workflow record
- compiled task records
- compiled subtask records
- hook lineage
- source document hashes and roles
- compile failure history if applicable

## Failure cases that must be supported

- schema-invalid YAML
- override conflicts
- hook insertion conflicts
- missing referenced task or subtask definitions
- unresolved source role ambiguity
- recompile requested while the node still has an active authoritative run

## Active-run legality

- authoritative recompile must be rejected whenever the authoritative lifecycle or daemon state still indicates an active run
- the rejection must not erase or hide the currently inspectable workflow and source-discovery surfaces for that authoritative version

## Completion rule

The node version has exactly one authoritative compile result visible to users: either a compiled workflow snapshot or a durable compile-failure record with enough context to fix it.
