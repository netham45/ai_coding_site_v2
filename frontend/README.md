# Frontend Workspace

This directory is the canonical working directory for the website UI.

Phase `web/setup/00` freezes only the Node and package-runtime baseline.

It does not yet claim:

- Vite bootstrap
- React bootstrap
- Axios/query setup
- Playwright setup

## Canonical Phase-00 Commands

Run these from the repository root unless noted otherwise:

```bash
node -v
npm -v
cd frontend && npm install
```

## Current Workspace Contract

- package manager: `npm`
- runtime owner: local Node.js install
- frontend root: `frontend/`
- later app/framework bootstrapping lands in subsequent `plan/web/setup/*` phases

## Next Planned Setup Phases

- `plan/web/setup/01_vite_and_react_bootstrap.md`
- `plan/web/setup/02_axios_and_query_foundation.md`
- `plan/web/setup/03_playwright_bootstrap.md`
