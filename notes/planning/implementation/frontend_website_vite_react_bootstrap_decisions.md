# Frontend Website Vite And React Bootstrap Decisions

## Purpose

Record the implementation decisions made during web setup phase 01 so later setup phases build on one stable frontend app entrypoint rather than reworking the bootstrap repeatedly.

## Phase-01 Decisions

### App bootstrap stack

The website bootstrap app now uses:

- Vite
- React

This is the canonical frontend app runtime for the website effort.

### Initial entrypoint

The frontend entrypoint is:

- `frontend/index.html`
- `frontend/src/main.jsx`

The React shell root is:

- `frontend/src/App.jsx`

### Initial shell contract

Phase 01 intentionally renders only a placeholder operator shell.

The shell is not yet:

- a routed application
- a daemon-connected application
- an Axios or query-aware application
- a feature-complete operator surface

Its job is narrower:

- prove Vite boots
- prove React renders
- provide one stable placeholder root for later setup phases

### Stable placeholder marker

The initial shell exposes:

- `data-testid="app-shell-placeholder"`

This gives later testing phases one stable bootstrap marker before richer route-level test ids exist.

### Bounded proof shape

Phase 01 uses a lightweight Node-side render check rather than bringing in a broader frontend test runner immediately.

Current proof approach:

- import the root shell component directly
- render it through `react-dom/server`
- assert the placeholder marker and heading are present

This keeps the bootstrap phase lighter while still proving that the shell renders.

### Canonical phase-01 commands

From the repository root:

```bash
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
```

These commands prove:

- dependencies resolve
- the placeholder shell renders in bounded proof
- the Vite bundle builds successfully

## Relationship To Later Phases

Phase 01 does not settle:

- routing
- React Router adoption
- Axios setup
- query/cache setup
- Playwright setup
- daemon dev proxy integration

Those belong to later setup phases and should reuse this bootstrap instead of replacing it casually.
