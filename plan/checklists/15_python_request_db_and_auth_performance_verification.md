# Checklist C15: Python Request, DB, And Auth Performance Verification

## Goal

Verify that the pinned FastAPI, synchronous DB access, and local-cookie auth posture holds under realistic load.

## Verify

- FastAPI request handling remains responsive with synchronous SQLAlchemy access under expected concurrency
- auth dependency or middleware overhead stays bounded on common request paths
- CLI token discovery and authenticated request flows remain fast enough for frequent orchestration polling
- no obvious threadpool starvation or avoidable request serialization appears in baseline daemon behavior

## Tests

- exhaustive concurrency, latency, and failure-mode tests around request handling, DB access, and auth flows
- performance checks for hot authenticated endpoints and repeated CLI polling paths

## Notes

- update stack/auth/performance notes if the sync-on-async posture proves insufficient and the stack needs to move to a different DB access model
