# Setup Bootstrap Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/00_project_bootstrap.md`.

## Decisions

### Python packaging

- use a `src/` layout rooted at `src/aicoding`
- expose a console entrypoint named `aicoding`
- keep the CLI framework minimal during bootstrap by using the standard library

### Database posture

- PostgreSQL remains the required durable database
- bootstrap code reads the connection string from `AICODING_DATABASE_URL`
- phase `S01` now requires a live PostgreSQL database for migration and connection-lifecycle verification
- Alembic is initialized now so later schema work lands on a stable migration path
- database bootstrap includes a minimal `bootstrap_metadata` table so migration repeatability can be tested against a real revision path instead of an empty migration chain

### Daemon posture

- FastAPI app factory lives at `aicoding.daemon.app:create_app`
- a bearer token dependency exists now as the minimum auth foundation
- bootstrap uses an environment-backed token while the local cookie-file lifecycle is deferred to later setup phases

### Resource posture

- packaged built-in YAML and prompt assets live under `src/aicoding/resources`
- project-local and override directories exist in the packaged resource tree for now so loader work can start from a stable path convention

### Test and performance posture

- pytest is configured immediately for unit, integration, and performance tests
- performance checks are bootstrap smoke thresholds, not benchmark-grade regressions
- database lifecycle tests reset the `public` schema between runs rather than creating and dropping databases, because that is compatible with a non-superuser owner account in local development

## Follow-up

The daemon auth note in `AGENTS.md` expects startup to create or load a local magic-cookie file. Bootstrap only establishes the environment-backed dependency and placeholder path configuration. That fuller token-file lifecycle should be completed in `plan/setup/10_fastapi_dependency_and_auth_foundation.md`.
