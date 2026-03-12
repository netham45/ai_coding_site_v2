# Frontend Website Browser Harness Matrix Adoption

## Context

This note records the current adopted browser-test harness and Playwright target matrix for the website effort.

## Adopted Harness

### Browser layer

The browser proof uses:

- real Chromium via Playwright
- the real built frontend app served through `vite preview`
- deterministic daemon-presented HTTP scenarios

### Daemon-side scenario layer

The current adopted scenario server is the mock-daemon HTTP surface under:

- `frontend/mock-daemon/scenarios.js`
- `frontend/mock-daemon/server.mjs`

This is not frontend-only request interception.

It is a deterministic HTTP process that serves daemon-owned response shapes over the normal browser API contract.

### Runtime assumptions

The browser tests seed runtime config through browser storage for:

- API base URL
- bearer token

This keeps browser tests aligned with the central Axios session approach already adopted by the frontend.

## Adopted Playwright Matrix

### Current primary browser narratives

- project selection and top-level creation
- real repo-backed project selection and top-level creation against the daemon-served frontend
- tree rendering and tree navigation
- overview/runs/prompts/actions/provenance narrative
- prompt save-and-regenerate narrative
- full agreed-v1 action execution narrative
- workflow/summaries/sessions deep-link narrative
- blocked action state narrative
- empty project catalog narrative
- top-level creation validation failure narrative
- live-candidate-blocked prompt editing narrative
- route back/forward navigation narrative
- representative loading, empty, and error state narratives for projects, tree, actions, and prompts

### Current browser test files

- `frontend/tests/e2e/smoke.spec.js`
- `frontend/tests/e2e/coverage-gaps.spec.js`
- `frontend/tests/e2e/residual-gaps.spec.js`

## Current Remaining Matrix Gaps

The remaining browser-proof gaps are no longer about the agreed v1 action table or the basic shared-state primitives.

They are now mainly:

- screenshot review automation beyond simple artifact capture
- deeper non-v1 route/tab permutation closure
- broader real-daemon browser narratives beyond the repo-backed project-start checkpoint

## Conclusion

The browser harness and E2E matrix phase is now satisfied in implementation terms.

It should be understood as:

- adopted
- implemented
- browser-proven for the main operator narratives

It should not be overstated as exhaustive closure for every possible browser permutation.
