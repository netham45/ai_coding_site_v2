# YAML Schema And Field Rigidity Phase 2 Gap Taxonomy Note

## Purpose

This note records the Phase 2 gap taxonomy for `plan/tasks/2026-03-11_yaml_schema_and_field_rigidity_investigation.md`.

Phase 1 established the active YAML families and the current proving layers. Phase 2 separates true rigidity gaps from families that are already defended through grouped library or compile/runtime proof.

## Classification Rules Used

Each YAML family is classified into one of these buckets.

### Bucket A: Schema-only or near-schema-only

The family has explicit validation models, but little or no family-specific proving beyond generic acceptance/rejection.

### Bucket B: Grouped-library covered but field-rigidity thin

The family is part of a stronger library-level proving surface, but many individual fields or per-document invariants are only defended indirectly.

### Bucket C: Runtime-sensitive and integration-covered, but still field-thin

The family affects compile-time or runtime behavior and does have integration proof, but the integration layer is carrying too much of the proving burden for family-level fields.

### Bucket D: Already adequately grouped for current phase

The family already has a reasonable combination of schema validation, grouped library checks, and runtime-adjacent proof for the current implementation phase. It may still merit more tests later, but it is not the first rigidity gap.

## Family Taxonomy

### Bucket A: Schema-only or near-schema-only

- `rectification_definition`
  - current proof:
    - generic schema validation
    - one negative validator test for duplicate subtask ids
  - why it is a true gap:
    - no dedicated library inspector
    - no direct runtime or CLI proving surface for authored rectification docs as a family
    - meaningful fields like `trigger`, `entry_task`, and cross-reference assumptions are barely defended

- `environment_policy_definition`
  - current proof:
    - generic schema validation
    - one compile failure path for undeclared environment profile
  - why it is a true gap:
    - only two built-ins exist, but the family affects runtime isolation semantics
    - current proof is mostly one bad compile-path case rather than family-level rigidity
    - no dedicated family inventory or field-focused negative matrix

### Bucket B: Grouped-library covered but field-rigidity thin

- `validation_definition`
  - current proof:
    - generic schema validation
    - quality-library grouping
    - some task-level binding checks inside `validate_node`
  - why it is still a gap:
    - the family has many check variants, but the current tests do not exercise a rigid per-check matrix across the authored built-ins
    - the proving surface is stronger for the `ValidationCheckDefinition` model than for the authored validation-library documents as a family

- `runtime_definition`
  - current proof:
    - generic schema validation
    - operational-library grouping
    - runtime action refs must map to subtask assets
  - why it is still a gap:
    - grouped operational-library checks mostly prove presence and prompt/reference integrity
    - thresholds, commands, and action semantics are not yet defended with family-specific rigidity expectations across the authored runtime docs

- `project_policy_definition`
  - current proof:
    - generic schema validation
    - project policy resolution tests
    - source-lineage inclusion
    - flow-yaml contract proof
  - why it is still a gap:
    - the family is runtime-important, but its field-level proving is spread across policy resolution and flow tests
    - there is little direct rigidity around the authored document shape beyond one invalid node-kind case

- `override_definition`
  - current proof:
    - generic schema validation
    - source-lineage capture
    - compile application and flow-yaml contract proof
  - why it is still a gap:
    - the family is heavily compile-sensitive, but the current tests focus on happy-path application and a few failure cases
    - merge modes, target-family applicability, and field-addressed constraints are not covered as a deliberate family matrix

### Bucket C: Runtime-sensitive and integration-covered, but still field-thin

- `hook_definition`
  - current proof:
    - generic schema validation
    - operational-library grouping
    - compile/runtime integration through workflow compilation
    - prompt-asset validation
  - why it is not a first-tier gap:
    - the family already has real compile authority and library checks
  - remaining weakness:
    - per-hook field rigidity is still indirect, especially for `when`, `applies_to`, and `if` combinations

- `runtime_policy_definition`
  - current proof:
    - generic schema validation
    - operational-library grouping
    - effective-policy resolution
    - workflow compilation
  - why it is not a first-tier gap:
    - it already participates in meaningful runtime and compile surfaces
  - remaining weakness:
    - the tests do not yet read like a family-level field matrix for authored runtime policies

- `testing_definition`
  - current proof:
    - generic schema validation
    - quality-library grouping
    - test runtime and compile usage
  - why it is not a first-tier gap:
    - this family already gets runtime exercise through testing flows
  - remaining weakness:
    - authored testing docs do not yet have explicit built-in-by-built-in rigidity checks

- `docs_definition`
  - current proof:
    - generic schema validation
    - quality-library grouping
    - docs runtime usage
  - why it is not a first-tier gap:
    - compile/runtime adjacency is real
  - remaining weakness:
    - authored doc-definition fields are mostly defended through grouped checks rather than a dedicated family matrix

### Bucket D: Already adequately grouped for current phase

- `node_definition`
- `task_definition`
- `subtask_definition`
- `layout_definition`
- `review_definition`
- `prompt_reference_definition`

These families are not perfect, but they already have a stronger combined surface:

- explicit schema models
- dedicated grouped-library checks
- meaningful cross-reference assertions
- prompt-binding integrity where applicable
- real compile/runtime adjacency

They should not be the first target for the new rigidity batch.

## False Gaps To Avoid

The investigation found several places where adding more tests could easily become low-value duplication.

### False gap 1

Do not add one bespoke test per YAML file merely because the file exists.

The current architecture already groups structural, quality, and operational YAML intentionally. The next rigidity layer should stay family-based and invariant-based.

### False gap 2

Do not treat every integration proof as missing just because the family lacks a dedicated CLI command.

Some families are correctly exercised through workflow compilation, policy resolution, source lineage, or downstream runtime components. The question is whether the right invariant is being proved, not whether every family has a bespoke endpoint.

### False gap 3

Do not duplicate prompt-pack tests as YAML rigidity tests unless the YAML family itself owns the prompt binding.

Prompt-bearing YAML should keep prompt-binding assertions where the YAML-to-prompt contract actually matters:

- review definitions
- hook definitions
- prompt-reference definitions
- prompt-bearing subtasks and tasks through library checks

## Recommended Priority Order For Implementation Planning

### Priority 1

- `rectification_definition`
- `environment_policy_definition`
- `validation_definition`

Reason:

- weak family-level rigidity
- meaningful operational effect
- relatively bounded family surface

### Priority 2

- `runtime_definition`
- `project_policy_definition`
- `override_definition`

Reason:

- important compile/runtime effect
- current proof is spread across several tests rather than expressed as family-level rigidity

### Priority 3

- `hook_definition`
- `runtime_policy_definition`
- `testing_definition`
- `docs_definition`

Reason:

- already meaningfully defended, but still candidates for a later richer family matrix

## Phase 2 Findings

### Main finding 1

The biggest missing piece is not raw schema validation. It is family-specific rigidity for authored YAML families that currently rely on:

- one or two targeted negative tests
- grouped library inspection
- or successful workflow compile as indirect proof

### Main finding 2

The next implementation plan should be structured by family bucket, not by test file.

That will keep the work aligned with the actual risk:

- low-level field validators for weaker families
- grouped built-in library tests for authored family inventories
- integration proof only where the family genuinely affects daemon or CLI behavior

### Main finding 3

The future rigidity batch should preserve the code-vs-YAML boundary.

YAML tests should prove declarative structure, references, and policy invariants. They should not try to re-prove every daemon coordination rule that properly belongs in code.

## Next Step

Phase 3 should turn this taxonomy into a concrete rigid-test strategy by family:

- which families need schema-negative expansion
- which families need family-level authored-library rigidity tests
- which families need daemon/CLI integration additions
- which families are intentionally left covered by grouped-library and compile/runtime proof for now
