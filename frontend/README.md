# Frontend Workspace

This directory is the canonical working directory for the website UI.

Phase `web/setup/00` freezes only the Node and package-runtime baseline.

Phase `web/setup/01` now adds:

- Vite bootstrap
- React bootstrap
- placeholder app shell
- bounded render proof

Phase `web/setup/02` now adds:

- central Axios client
- shared TanStack Query foundation
- initial feature API-module skeleton

Phase `web/setup/03` now adds:

- Playwright bootstrap
- base browser-test config
- one smoke browser test

Phase `web/setup/04` now adds:

- deterministic mock-daemon scenario server
- project/tree/action bootstrap scenarios
- HTTP proof for deterministic daemon-shaped responses

Phase `web/setup/05` now adds:

- route skeleton
- persistent shell layout
- shared loading/empty/error/status primitives

It still does not yet claim:

- full live-daemon browser verification matrix

## Runtime Access

Normal operator/runtime use now has two distinct modes:

- daemon-served runtime:
  - run the daemon
  - open `http://127.0.0.1:8000/projects`
  - the daemon-served HTML injects the same-origin API base URL and bearer token automatically
- Vite development runtime:
  - run `cd frontend && npm run dev`
  - open `http://127.0.0.1:5173/projects`
  - set `aicoding.apiBaseUrl` and `aicoding.apiToken` in browser storage or use Vite env overrides when you need to talk to a daemon or mock daemon

If the daemon-served website returns a compiled-asset error, rebuild the frontend first:

```bash
cd frontend && npm run build
```


## Canonical Phase-00 Commands

Run these from the repository root unless noted otherwise:

```bash
node -v
npm -v
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npx playwright install chromium
cd frontend && npm run test:e2e
```

## Current Workspace Contract

- package manager: `npm`
- runtime owner: local Node.js install
- frontend root: `frontend/`
- Vite entrypoint: `index.html`
- React entrypoint: `src/main.jsx`
- placeholder shell: `src/App.js`
- central client: `src/lib/api/client.js`
- query provider: `src/lib/query/QueryProvider.js`
- query keys: `src/lib/query/keys.js`
- Playwright config: `playwright.config.js`
- smoke browser test: `tests/e2e/smoke.spec.js`
- mock daemon server: `mock-daemon/server.mjs`
- mock daemon scenarios: `mock-daemon/scenarios.js`
- router builder: `src/routes/router.js`
- shared primitives: `src/components/primitives/*`
- later routing/data/testing phases land in subsequent `plan/web/setup/*` phases

## Next Planned Setup Phases

- `plan/web/setup/01_vite_and_react_bootstrap.md`
- `plan/web/setup/02_axios_and_query_foundation.md`
- `plan/web/setup/03_playwright_bootstrap.md`
