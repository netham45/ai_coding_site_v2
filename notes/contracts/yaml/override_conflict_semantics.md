# Override Conflict Semantics

## Purpose

This document defines how override files should behave when they modify built-in or project-local YAML definitions.

The design already assumes:

- built-in YAML exists
- project-local extensions exist
- project-local overrides exist
- compilation resolves these into immutable workflows

What remained underspecified was:

- exactly how overrides merge
- when overrides replace versus append versus deep-merge
- what counts as an override conflict
- when compilation must fail

This document makes those rules explicit enough to support the v2 YAML and compilation model.

Related documents:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Implementation staging note:

- the current implementation now applies override files during the compiler's explicit `override_resolution` stage and records failures as durable compile failures with target family and target ID
- the current implementation enforces top-level field merge modes per YAML family rather than arbitrary nested patch paths
- identity fields such as document `id` and node `kind` are currently treated as immutable during override resolution even if the broader spec later relaxes some of those cases
- create-if-missing override behavior remains unsupported

---

## Core Rule

Overrides must be deterministic, auditable, and safe.

That means:

- the same source set must always resolve to the same merged result
- every override contribution must be traceable
- invalid or ambiguous merges must fail compilation
- override behavior must not rely on hidden field-by-field intuition

---

## Override Layers

The resolution order should remain:

1. built-in base definitions
2. project-local extension definitions
3. project-local override definitions

Rule:

- extensions add new definitions
- overrides modify existing definitions

An override that targets a definition that does not exist should fail unless the family explicitly allows create-if-missing behavior.

Recommended default:

- no create-if-missing for overrides

---

## Override Targeting Rule

Every override should identify:

- target family
- target ID
- merge mode
- override payload

This must be enough to determine exactly what document is being modified and how.

If multiple source definitions with the same family and ID exist before override resolution:

- that should itself be treated as an ambiguity or extension conflict unless the system has a documented precedence rule for those duplicates

---

## Merge Modes

The system should support a small explicit set of merge modes.

### 1. `replace`

Meaning:

- replace the targeted field or object entirely

Use when:

- value is atomic
- value should not be merged structurally

Examples:

- replacing `main_prompt`
- replacing `entry_task`
- replacing a scalar policy field

### 2. `deep_merge`

Meaning:

- merge object keys recursively

Use when:

- the target is a mapping/object
- child keys can be safely merged

Examples:

- merging node policy objects
- merging environment maps
- merging input flags

### 3. `append_list`

Meaning:

- append items to an existing list

Use when:

- target list is additive
- duplicate handling is defined or acceptable

Examples:

- appending hook refs
- appending review refs
- appending testing refs

### 4. `replace_list`

Meaning:

- replace the entire target list

Use when:

- order matters heavily
- additive merge would be unsafe

Examples:

- replacing ordered task lists
- replacing subtask lists

---

## Recommended Field-Level Merge Catalog

The following default guidance should apply unless a family explicitly says otherwise.

## Node definition fields

### Replace by default

- `id`
- `kind`
- `tier`
- `main_prompt`
- `entry_task`

### Deep-merge by default

- `parent_constraints`
- `child_constraints`
- `policies`

### Append-list by default

- `hooks`

### Replace-list by default

- `available_tasks`

Reason:

- task order and selection are important enough that partial append semantics may be too implicit by default

## Task definition fields

### Replace by default

- `id`
- `name`
- `description`
- `policy.on_failure`

### Deep-merge by default

- `policy`

### Append-list by default

- `uses_reviews`
- `uses_testing`
- `uses_docs`

### Replace-list by default

- `subtasks`
- `applies_to_kinds`

Reason:

- subtask order is too important to merge implicitly without explicit replacement

## Layout definition fields

### Replace-list by default

- `children`

Reason:

- layout child order, IDs, and dependencies are structurally important enough that additive list mutation is risky

## Hook definition fields

### Replace by default

- `when`

### Deep-merge by default

- `applies_to`
- `if`

### Replace-list by default

- `run`

## Review/testing/docs definition fields

### Replace by default

- `scope`
- `description`
- `prompt`

### Deep-merge by default

- `applies_to`
- `inputs`
- `retry_policy`
- `pass_rules`
- `rebuild_policy`
- `on_result`

### Replace-list by default

- `criteria`
- `commands`
- `outputs`

---

## Conflict Types

The system should treat at least the following as override conflicts.

## C01. Missing target

The override references a family/id pair that does not exist.

Default action:

- fail compilation

## C02. Type mismatch

The override applies a merge mode that is incompatible with the target field type.

Examples:

- `deep_merge` against a scalar
- `append_list` against a mapping

Default action:

- fail compilation

## C03. Ambiguous duplicate target

More than one candidate document exists for the same family/id after source loading but before override resolution.

Default action:

- fail compilation unless precedence is explicitly defined

## C04. Invalid merged schema

The merged result violates schema validation.

Default action:

- fail compilation

## C05. Forbidden field override

An override attempts to modify a field classified as immutable or system-owned.

Examples:

- compiled-only fields
- lineage-only fields

Default action:

- fail compilation

## C06. Order-sensitive partial merge without explicit intent

An override tries to alter an ordered structure in a way that produces ambiguous ordering.

Examples:

- additive mutation of subtask order
- additive mutation of ordered children without explicit semantics

Default action:

- fail compilation or require `replace_list`

---

## Compile Failure Rule

Override conflicts should be compile-time failures, not runtime surprises.

If an override conflict occurs:

1. compilation stops
2. the failure should be recorded durably if compile-failure persistence is implemented
3. the operator should be able to inspect:
   - target family
   - target ID
   - merge mode
   - conflicting field
   - reason for failure

The system should prefer explicit failure over “best effort” merging.

---

## Examples

## Example 1: Valid deep merge

Base:

```yaml
node_definition:
  id: phase
  policies:
    auto_run_children: true
    require_review_before_finalize: true
```

Override:

```yaml
override_definition:
  target_family: node_definition
  target_id: phase
  merge_mode: deep_merge
  value:
    policies:
      auto_run_children: false
```

Resolved result:

```yaml
node_definition:
  id: phase
  policies:
    auto_run_children: false
    require_review_before_finalize: true
```

## Example 2: Invalid append to ordered subtasks

Base:

```yaml
task_definition:
  id: review_node
  subtasks:
    - id: gather_context
    - id: run_review
```

Override:

```yaml
override_definition:
  target_family: task_definition
  target_id: review_node
  merge_mode: append_list
  value:
    subtasks:
      - id: extra_step
```

Result:

- invalid by default

Reason:

- `subtasks` is a replace-list field, not append-list by default

## Example 3: Missing target

Override:

```yaml
override_definition:
  target_family: review_definition
  target_id: nonexistent_review
  merge_mode: replace
  value:
    description: New description
```

Result:

- compile failure

---

## Suggested Override Resolution Pseudocode

```python
def apply_override(base_doc, override):
    target = find_target_document(base_doc.family, override.target_id)
    if target is None:
        raise OverrideConflict("missing_target")

    merge_catalog = get_family_merge_catalog(base_doc.family)
    validated_payload = validate_override_fields(override.value, merge_catalog)

    merged = merge_using_mode(
        target_doc=target,
        payload=validated_payload,
        merge_mode=override.merge_mode,
        merge_catalog=merge_catalog,
    )

    validate_schema(merged)
    return merged
```

The real implementation should produce richer conflict metadata, but this captures the decision boundary.

---

## DB And Lineage Implications

The database should preserve enough lineage to explain:

- which override files applied
- which target definition each override affected
- which source role each override had
- which content hash each override contributed

If compile-failure persistence is added, it should also preserve:

- failed override target
- merge mode
- failure reason

---

## CLI Implications

The CLI should allow operators to inspect:

- source YAML
- resolved YAML
- source document lineage
- active overrides

Likely useful additions:

- `ai-tool overrides explain --node <id>`
- `ai-tool yaml compile-check --node <id>`

If names differ, these capabilities should still exist.

---

## Open Decisions Still Remaining

### D01. Duplicate handling in append-list mode

Should appended items deduplicate automatically?

Recommended default:

- no automatic deduplication unless the family defines key-based uniqueness

### D02. Create-if-missing override behavior

Should overrides ever create missing targets?

Recommended default:

- no

### D03. Cross-family override references

Should one override be able to reference another family indirectly?

Recommended default:

- avoid this in initial implementation

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/yaml/yaml_schemas_spec_v2.md`
2. future implementation-grade compile logic notes
3. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the override-conflict gap.

---

## Exit Criteria

This appendix is complete enough when:

- merge modes are explicit
- field-level merge defaults are explicit enough to prevent ambiguity
- conflict classes are explicit
- compile-failure behavior is explicit

At that point, override semantics are concrete enough to support safe YAML-driven orchestration.
