# Frontend Website Mock Daemon Harness Decisions

## Purpose

Record the implementation decisions made during web setup phase 04 so later browser-proof phases build on one deterministic daemon-shaped scenario harness.

## Phase-04 Decisions

### Harness shape

Phase 04 uses:

- a lightweight repo-local HTTP scenario server under `frontend/mock-daemon/`

It is not the full live daemon.

It is the bootstrap harness that serves daemon-shaped responses over real HTTP for browser-facing setup proof.

### Current scenario families

The initial scenario set includes:

- one project-catalog scenario
- one small healthy tree scenario
- one small action-catalog scenario

These are enough to prove the harness shape without expanding into full feature coverage yet.

### Auth posture

The bootstrap harness uses the same basic browser-client shape:

- bearer token required on requests

The token is fixed and deterministic for setup proof.

This keeps the harness aligned with the daemon-client model without requiring full runtime auth plumbing yet.

### Current proof shape

Phase 04 uses a deterministic Node-side proof script that:

- boots the scenario server
- calls project-catalog HTTP route
- calls tree HTTP route
- calls action-catalog HTTP route
- verifies the deterministic payload shapes

This is still a setup-phase proof, not the final Playwright or real-daemon verification story.
