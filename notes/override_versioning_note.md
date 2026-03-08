# Override Versioning Note

## Purpose

This note captures a recommended versioning and compatibility model for built-in YAML definitions and project-local overrides.

The goal is to reduce confusion when built-in definitions evolve over time while projects continue to carry local overrides, hooks, and customizations.

Related documents:

- `notes/yaml_schemas_spec_v2.md`
- `notes/override_conflict_semantics.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

---

## Core Problem

If the system ships built-in YAML definitions and allows project-local overrides, then built-in definitions will eventually change.

Without explicit versioning and compatibility metadata, projects can end up with:

- stale overrides targeting old built-in behavior
- confusing compile failures after upgrades
- subtle semantic drift where overrides still apply but no longer mean what the project author expected
- poor operator visibility into what changed relative to the built-in base

The system should make that drift visible and diagnosable.

---

## Recommended Decisions

### 1. Version built-in YAML families explicitly

Built-in YAML families should carry explicit version identity.

This versioning should allow the system to distinguish:

- schema/runtime generation
- built-in library generation
- individual built-in document versions where needed

At minimum, the system should be able to answer:

- which built-in YAML version a node compiled against
- which built-in document revision an override targeted

### 2. Persist the exact built-in version used for compilation

When a node version compiles its workflow, the system should durably preserve:

- built-in library version
- source document paths
- source hashes
- resolved merged YAML

This ensures later inspection can answer not just "what override existed" but "what built-in base it was applied to."

### 3. Allow overrides to declare compatibility targets

Project-local overrides should be able to declare compatibility metadata such as:

- minimum supported schema/runtime version
- targeted built-in library version or version range
- targeted document family and base document ID

This does not need to become an overcomplicated package manager.

The purpose is simply to let the compiler and CLI detect when an override is probably stale or misaligned.

### 4. Warn on stale or weakly compatible overrides

If an override appears to target an older built-in version or an incompatible document shape, the system should emit a clear warning or compile failure depending on severity.

Examples:

- warning when the override still applies cleanly but targets an older built-in version
- compile failure when the override references fields or insertion points that no longer exist
- warning when compatibility metadata is missing and the system must fall back to best-effort matching

### 5. Provide override diff and introspection surfaces

The CLI should provide a way to inspect what an override changed relative to its built-in base.

At minimum, the system should support a query that can show:

- built-in base document
- override document
- resolved merged output
- fields added, removed, or replaced by the override
- compatibility/version metadata

This is important for debugging, audits, and upgrade workflows.

---

## Suggested Metadata Shape

The exact YAML fields can change, but the model likely needs metadata shaped roughly like:

```yaml
override_definition:
  id: project.review.override
  target:
    family: task_definition
    document_id: review_node
  compatibility:
    min_schema_version: 2
    built_in_version: "2.x"
  merge_mode: replace_fields
  changes:
    ...
```

This metadata should remain simple and diagnostic rather than trying to encode every possible policy.

---

## Persistence Expectations

The compiled workflow lineage should preserve enough information to answer:

- which built-in base document was used
- which built-in version it came from
- which overrides were applied
- whether compatibility warnings were raised
- what the resolved merged result was

If warning/failure diagnostics are generated during compile, those should be durable enough for later inspection.

---

## CLI Expectations

Useful future CLI surfaces likely include:

- `ai-tool yaml builtins show --family <family> --id <id>`
- `ai-tool yaml override show --path <path>`
- `ai-tool yaml override diff --path <path>`
- `ai-tool workflow sources --node <id>`

These do not need to be final command names. The important part is the capability.

---

## Recommended Stance

The system should not silently assume that old overrides remain valid forever.

Recommended default:

- version built-in YAML explicitly
- preserve the exact built-in version used at compile time
- allow overrides to declare compatibility intent
- warn clearly on stale overrides
- expose override-vs-base diffs through CLI

That gives projects room to customize aggressively without making override drift invisible.
