# FastAPI Dependency And Auth Foundation Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/10_fastapi_dependency_and_auth_foundation.md`.

## Decisions

### Auth lifecycle

- daemon startup now creates or loads the local magic-cookie token file at the configured path
- if the file already exists, the daemon reuses it as the runtime bearer token source
- if the file does not exist, the daemon seeds it from `AICODING_AUTH_TOKEN` when present, otherwise it generates a random token and writes it locally
- the daemon validates requests against the runtime token file rather than the raw environment value so CLI and daemon stay aligned

### Dependency posture

- FastAPI auth now uses a request-backed dependency with `HTTPBearer` instead of manually parsing the header string
- auth context is stored in app state as non-secret metadata only: token file path and token source
- protected endpoints continue to declare auth through explicit dependencies rather than hidden middleware

### Local-path posture

- daemon token-file creation ensures the parent directory exists
- the implementation applies best-effort local-only permissions to the token directory and file on POSIX hosts
- token values are never returned through CLI or daemon payloads

### Test and performance posture

- coverage now includes startup token-file creation, generated-token fallback, invalid-token rejection, missing-header rejection, bad-path handling, and file permission expectations
- performance checks now include auth-context initialization as a startup-sensitive path
