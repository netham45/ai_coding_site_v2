# Local App Startup And Debug Contract

## Purpose

Define the future contract for how collaborative-design tasks would reliably boot, inspect, and debug a local application instead of rediscovering startup behavior ad hoc.

This is a working note, not an implementation contract.

## Core Problem

A collaborative-design task is not useful if it can edit UI code but cannot reliably:

- install dependencies
- start the right dev servers
- start dependent services
- authenticate into the app
- reach the page worth reviewing
- reproduce the same state later

The system needs durable startup and debug knowledge, not chat memory.

## Main Recommendation

The repository should eventually treat local app startup and UI-debug entry as first-class runtime metadata.

That metadata should answer:

- how to install
- how to boot
- how to detect readiness
- how to stop
- how to run in seeded or mocked mode
- how to open a reviewable UI state

## Why This Cannot Be Left Ad Hoc

If the AI has to rediscover startup commands every time, failure modes are predictable:

- wrong port
- wrong service order
- stale database state
- broken login assumptions
- clicking through the wrong path
- reviewing the wrong page version

That makes the workflow slow and non-reproducible.

## Required Metadata Categories

The future contract should probably capture:

- install command
- primary frontend start command
- backend or API start commands when required
- supporting services such as database or queue startup commands
- readiness checks
- base URLs
- auth posture for local review
- fixture or seed modes
- mock modes
- teardown behavior

## Possible Declarative Shape

This could later become a family such as:

- `ui_runtime_contract`

Example draft:

```yaml
kind: ui_runtime_contract
id: web_app_local_dev
install:
  command: pnpm install
frontend:
  start_command: pnpm dev
  readiness_url: http://127.0.0.1:3000/
backend:
  start_command: pnpm api:dev
  readiness_url: http://127.0.0.1:4000/health
supporting_services:
  - name: postgres
    start_command: docker compose up -d postgres
auth:
  mode: local_test_user
  seed_command: pnpm seed:test-user
review_modes:
  - real_backend
  - fixture_seeded
  - mock_api
teardown:
  command: pnpm dev:stop
```

## Readiness And Health

The future system should not assume a process is ready just because it was launched.

It should have explicit readiness checks such as:

- health endpoint
- root-page load
- log marker
- socket or port readiness

## Debug-Oriented Requirements

To be useful for design work, the contract should also capture:

- how to open source maps or dev overlays if needed
- how to capture browser console errors
- how to capture network failures
- how to preserve screenshots or traces
- how to stop and restart cleanly

## Relationship To Canonical Commands

This future contract fits the repository rule that startup and verification commands should be documented canonically rather than rediscovered.

The difference is that collaborative design would need runtime-usable command metadata, not only human-readable docs.

## Recommended Next Step

Pair this with a future `ui_review_scenario` concept that says how to get from a running app to a specific reviewable page state.
