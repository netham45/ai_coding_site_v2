# Frontend Website Setup Baseline Decisions

## Purpose

Record the implementation decisions made during web setup phase 00 so later frontend setup phases do not need to rediscover the workspace boundary or package-runtime commands.

## Baseline Decisions

### Canonical frontend working directory

The website UI lives under:

- `frontend/`

This directory is the package boundary for the browser client.

The repository should not split the initial website bootstrap across multiple frontend roots unless a later note explicitly revisits that decision.

### Package manager

The canonical package manager is:

- `npm`

Reasoning:

- Node and npm are already available locally
- phase 00 only needs a minimal and reliable package baseline
- choosing npm avoids introducing extra package-manager doctrine before the app exists

### Initial package-runtime scope

Phase 00 intentionally freezes only:

- Node runtime availability
- npm availability
- frontend package boundary
- minimal package manifest
- initial artifact-ignore rule

Phase 00 intentionally does not claim:

- Vite bootstrap
- React bootstrap
- frontend build scripts
- Axios or query setup
- Playwright setup

### Canonical commands for phase 00

From the repository root:

```bash
node -v
npm -v
cd frontend && npm install
```

These commands prove:

- Node is available
- npm is available
- the frontend package manifest is valid
- a lockfile can be created successfully for the frontend workspace

## Relationship To Daemon Hosting

This phase does not yet implement daemon asset serving or dev proxy behavior.

It does freeze the architectural expectation that:

- the website remains a daemon client
- later dev-mode integration may proxy through the daemon to the frontend dev server
- later non-dev integration may serve built frontend assets through the daemon

Those behaviors belong to later setup and feature phases, not to the runtime baseline phase.

## Follow-On Phases

The next setup phases should build on this baseline in order:

1. `plan/web/setup/01_vite_and_react_bootstrap.md`
2. `plan/web/setup/02_axios_and_query_foundation.md`
3. `plan/web/setup/03_playwright_bootstrap.md`
