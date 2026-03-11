# Frontend Website Playwright Bootstrap Decisions

## Purpose

Record the implementation decisions made during web setup phase 03 so later browser-proof and daemon-backed harness phases build on one stable Playwright baseline.

## Phase-03 Decisions

### Browser test framework

The website uses:

- Playwright

This is the canonical browser E2E foundation for the website effort.

### Current bootstrap scope

Phase 03 intentionally establishes only:

- Playwright dependency and scripts
- base Playwright config
- artifact output paths
- one smoke browser test against the existing placeholder shell

Phase 03 intentionally does not yet establish:

- daemon-backed mock scenarios
- route-by-route browser coverage
- screenshot review workflows
- full action and mutation E2E coverage

Those belong to later planned phases.

### Artifact paths

Phase 03 freezes these frontend-local artifact paths:

- `frontend/test-results/`
- `frontend/playwright-report/`

### Smoke-test contract

The smoke browser test proves only that:

- the built frontend can be served and opened
- the placeholder shell renders
- the stable placeholder test id is visible in a real browser

It is a bootstrap proof, not a substitute for the later daemon-backed browser matrix.

### Current server strategy

Phase 03 uses Playwright `webServer` to start:

- `npm run preview -- --host 127.0.0.1 --port 4173`

This keeps the smoke proof close to the built-asset path without yet introducing daemon hosting or proxy behavior.

### Environment requirement discovered during bootstrap

The Playwright smoke proof depends on native browser libraries being available on the host.

In this environment:

- `npx playwright install chromium` succeeds
- browser launch still fails because shared libraries such as `libnspr4.so` are missing
- `npx playwright install-deps chromium` requires privileged `sudo` access and cannot complete inside the current session

That means the Playwright bootstrap artifacts are implemented, but the final smoke proof remains environment-blocked until the host browser dependencies are installed.
