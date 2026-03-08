# Invalid Dependency Graph Flow

Sources:

- `notes/invalid_dependency_graph_handling.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

## Scenario

Three invalid dependency cases are tested against a would-be child layout:

1. missing target dependency
2. cycle
3. cross-version ambiguity during rectification

The runtime must fail fast and visibly.

## Shared setup

Parent node:

- `plan_v1`

Relevant CLI commands:

```text
ai-tool layout show --node plan_v1
ai-tool layout validate --node plan_v1
ai-tool node dependency-validate --node plan_v1
ai-tool node events --node plan_v1
ai-tool node pause-state --node plan_v1
```

## Case A: missing target dependency

### YAML read

```yaml
layout_definition:
  children:
    - id: task_a
      kind: task
      dependencies:
        - task_missing
```

### Relation checks

1. layout child IDs loaded: `task_a`
2. dependency edge references `task_missing`
3. `task_missing` not found in same layout child set
4. validation stops before materialization

### DB writes

1. `subtask_attempts`
   - insert validation-attempt row for the relevant parent compiled subtask
2. `validation_results`
   - insert failure:
     - `check_type = yaml_schema` or dependency validation subtype
     - `status = FAIL`
     - evidence references missing target `task_missing`
3. `summaries`
   - insert parent-visible validation summary
4. `workflow_events`
   - insert `layout_validation_failed`

### Writes that must not happen

- no `node_versions` rows for child nodes
- no `node_children` rows
- no `node_dependencies` rows
- no `node_version_lineage` rows

### CLI result

```json
{
  "status": "FAIL",
  "dependency_validation": "missing_target",
  "summary": "Dependency target task_missing was not found in the layout child set."
}
```

## Case B: cycle

### YAML read

```yaml
layout_definition:
  children:
    - id: task_a
      kind: task
      dependencies: [task_b]
    - id: task_b
      kind: task
      dependencies: [task_a]
```

### Relation checks

1. both target IDs exist
2. both edges are sibling-relative and nominally allowed
3. dependency graph traversal detects cycle:
   - `task_a -> task_b -> task_a`
4. validation fails before materialization

### DB writes

1. `subtask_attempts`
   - insert validation attempt
2. `validation_results`
   - insert failure with cycle evidence
3. `summaries`
   - insert failure summary
4. `workflow_events`
   - insert dependency graph failure event

### Writes that must not happen

- no child node rows
- no dependency edge persistence
- no scheduling classification events

### CLI result

```json
{
  "status": "FAIL",
  "dependency_validation": "invalid_cycle",
  "summary": "Child dependency graph contains a cycle between task_a and task_b."
}
```

## Case C: cross-version ambiguity during rectification

### Runtime state read

Authoritative mapping:

- logical `task_parser` -> `task_parser_v1`

Latest created mapping:

- logical `task_parser` -> `task_parser_v2`

Candidate lineage in progress:

- `plan_v2` is rebuilding
- layout or dependency reference uses logical child identity without explicit authoritative resolution in candidate context

### Relation checks

1. dependency target can map to more than one node version
2. runtime checks authoritative lineage
3. runtime checks candidate lineage
4. target selection is not unambiguous for the current validation scope
5. runtime must fail or pause, not guess

### DB writes

1. `validation_results`
   - insert failure referencing ambiguous target
2. `workflow_events`
   - insert `dependency_target_ambiguous`
3. `summaries`
   - insert operator-visible summary
4. optional:
   - `node_run_state`
     - update parent to `PAUSED_FOR_USER` if policy routes ambiguity to pause

### CLI result

```json
{
  "status": "FAIL",
  "dependency_validation": "cross_version_ambiguity",
  "summary": "Dependency target task_parser does not resolve unambiguously to one authoritative node version."
}
```

## Result

This simulation makes the anti-knot rule explicit:

- invalid graphs fail before materialization
- no partial child tree becomes authoritative
- runtime refuses ambiguous dependency resolution during mixed old/new lineage states

## Hole still visible

The notes still do not freeze one canonical built-in recovery branch after dependency validation failure:

- auto-revise layout
- route into a revise task
- pause for user immediately

This simulation assumes validation failure is visible first and recovery is policy-driven second.
