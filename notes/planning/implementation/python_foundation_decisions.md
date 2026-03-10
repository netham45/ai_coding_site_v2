# Python Foundation Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/02_python_foundation.md`.

## Decisions

### Shared package foundations

- keep shared runtime helpers in top-level package modules rather than burying them inside only the CLI or only the daemon
- use one `Settings` model for both CLI and daemon startup
- treat logging, resource discovery, and auth-token loading as shared Python infrastructure

### CLI posture

- the CLI remains standard-library based for now
- command execution uses shared output and error formatting rather than command-specific `print` calls only
- direct database inspection commands still exist during bootstrap, but the authority note remains unchanged: future mutating operations should go through the daemon

### Daemon posture

- FastAPI lifespan owns shared app state initialization for settings, DB resources, and resource catalog loading
- synchronous SQLAlchemy access remains acceptable behind FastAPI request handling in this phase
- phase `S02` records that sync-DB-on-async-request assumptions must keep performance coverage, not just correctness coverage

### Resource posture

- packaged YAML, prompt, and docs directories now have a common loader interface
- path resolution rejects escaping the configured resource-root group

### Auth posture

- auth-token loading now supports both direct settings values and file-backed token lookup helpers
- daemon request auth still uses the configured token directly for now
- full daemon startup token-file creation remains deferred to `plan/setup/10_fastapi_dependency_and_auth_foundation.md`

