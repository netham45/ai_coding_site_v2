# Pydantic Settings And Model Foundation Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/09_pydantic_settings_and_model_foundation.md`.

## Decisions

### Settings posture

- environment variable compatibility stays flat for now so existing `AICODING_*` values continue to work without nested env rewrites
- `Settings` now validates core runtime values directly and exposes typed submodels for database, daemon, session, and auth configuration
- shared runtime code should prefer those typed submodels when consuming grouped configuration

### Model posture

- shared Pydantic models now inherit from a common strict base with `extra=\"forbid\"`
- daemon request and response models use that base for consistent validation and serialization behavior
- schema-compatibility and daemon-status payloads are now first-class typed API models instead of anonymous dictionaries

### YAML and prompt posture

- resource loading now exposes typed file descriptors and placeholder metadata models for YAML and prompt assets
- these models are intentionally lightweight and stop short of full schema validation or workflow compilation semantics

### Test and performance posture

- validation coverage now includes invalid settings values, strict model rejection of extra fields, and serialization stability for operator-facing payloads
- startup-sensitive performance checks now include settings parsing, model validation, and resource metadata construction
