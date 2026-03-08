# Phase S10: FastAPI Dependency And Auth Foundation

## Goal

Establish the FastAPI dependency graph and bearer-token auth model cleanly before feature endpoints accumulate.

## Scope

- Database: define request-scoped DB dependency injection and auth-related DB access boundaries if needed.
- CLI: ensure the CLI can discover and send the local magic-cookie bearer token consistently.
- Daemon: implement FastAPI dependency injection structure, bearer-token auth dependency/middleware, and local token file lifecycle.
- YAML: no YAML semantics beyond possible runtime policy references later.
- Prompts: no prompt semantics beyond future CLI/bootstrap references.
- Tests: exhaustively test token creation/loading, missing-token handling, bad-token rejection, auth dependency injection, and local path permission expectations.
- Performance: benchmark auth/dependency overhead on baseline requests.
- Notes: update auth and daemon notes if implementation changes token lifecycle or path assumptions.

## Exit Criteria

- bearer-token auth and FastAPI dependency patterns are explicit and fully test-backed.
