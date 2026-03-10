# SQLAlchemy Model And Session Foundation Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/07_sqlalchemy_model_and_session_foundation.md`.

## Decisions

### Metadata posture

- the repository now has one explicit SQLAlchemy metadata owner in `aicoding.db.base`
- metadata uses a naming convention for primary-key, foreign-key, unique, check, and index constraints so migrations stay predictable
- declarative models should continue to attach through that shared base rather than creating per-module metadata registries

### Session posture

- `query_session_scope(...)` is the default read/query boundary for CLI and daemon inspection paths
- `session_scope(...)` is the default transaction boundary for durable writes
- `nested_transaction(...)` is the explicit savepoint helper and rejects use when no outer transaction is active
- daemon-local transaction helpers were removed in favor of the shared DB session layer so write semantics do not drift

### Request and performance posture

- FastAPI request dependencies now reuse the shared query-session helper for consistent open/close behavior
- synchronous PostgreSQL access remains the default posture in this phase, but session-creation and roundtrip costs now have performance thresholds in pytest

### YAML and prompt posture

- this phase intentionally adds no new YAML semantics
- this phase intentionally adds no new prompt assets, but the session foundation remains compatible with later prompt-history and orchestration models
