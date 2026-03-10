# YAML Schema System Decisions

## Purpose

Capture implementation choices made while completing `plan/features/03_F04_yaml_schema_system.md`.

## Decisions

### Schema posture

- every authored built-in YAML family in the repository now has an explicit validator model and schema-family descriptor
- `node_definition` receives full field-level validation because it is already an active runtime surface
- the other built-in YAML families currently use strict scaffold schemas that validate the exact authored placeholder documents already present in the repo

### Staging posture

- richer family semantics for review, testing, docs, rectification, runtime policy, and prompt-linked YAML are intentionally deferred to later F04 sub-slices
- this phase makes those families explicit and testable now rather than leaving them implied, while avoiding invented semantics that the current notes have not fully frozen yet

### Runtime posture

- daemon now exposes authenticated YAML schema-family listing and document validation endpoints
- CLI validation requests go through the daemon so schema validation is auditable and follows the same authority boundary as other runtime-facing checks
- validation results are persisted in `yaml_schema_validation_records`

### YAML asset posture

- the repository now includes packaged schema-family metadata files under `src/aicoding/resources/yaml/schemas`
- these packaged schema descriptors document which validator model and built-in source glob each currently authored family uses
