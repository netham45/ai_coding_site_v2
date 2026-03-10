# Daemon Skeleton Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/04_daemon_skeleton.md`.

## Decisions

### Process posture

- the daemon remains a FastAPI application with a lifespan-managed startup and shutdown path
- startup initializes settings, logging, DB resources, the resource catalog, and a background-task registry placeholder

### Authority boundary

- placeholder mutating endpoints now exist under `/api/...` so the CLI can target the daemon boundary with validated request shapes
- mutation handlers currently acknowledge accepted requests without implementing orchestration semantics yet
- this preserves the daemon-as-authority model without pretending later runtime phases are already built

### Validation posture

- request validation failures are normalized into a structured JSON error payload
- DB-unavailable conditions are normalized into a daemon-specific `503` response instead of leaking raw SQLAlchemy errors

### Background-task posture

- background-task registration is scaffolded as an explicit registry on app state
- initial placeholders are `session_recovery` and `idle_nudge`

