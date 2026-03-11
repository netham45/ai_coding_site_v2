# Frontend Website UI Setup Family

## Purpose

Define the setup-family phases for the future website so the repo gains a stable frontend/tooling foundation before feature work begins.

This is a working note, not an implementation plan.

## Family Goal

Create a functioning React/Vite frontend workspace, wire it into the daemon development model, install Playwright, prove a trivial browser test, and lay out the app skeleton that later feature work will fill in.

This phase should also freeze the transport, query, and shared-state patterns the rest of the website will use.

## Setup Family Breakdown

The setup work should not be treated as one blob.

It should be broken into these phases:

1. Node and package-runtime baseline
2. Vite and React bootstrap
3. Axios and query foundation
4. Playwright bootstrap
5. mock daemon harness bootstrap
6. shell/router/shared primitive scaffold

## Required Setup Outcomes

The setup family as a whole should deliver all of the following:

- frontend package layout exists in the repo
- Vite + React app boots locally
- daemon dev mode can proxy to the Vite dev server
- non-dev mode can later be wired to daemon-served built assets
- central Axios client exists
- feature API module skeleton exists
- shared query/cache foundation exists
- Playwright is installed and runnable
- one hello-world or smoke browser test passes
- app shell skeleton exists
- route skeleton exists
- placeholder feature regions exist
- placeholder loading, empty, and error primitives exist
- frontend verification commands are documented

Each setup phase should also land with its own proof before moving on.

## Proposed Per-Phase Proof

### 1. Node and package-runtime baseline

Proof:

- Node version command passes
- package install succeeds
- frontend working directory is frozen

### 2. Vite and React bootstrap

Proof:

- Vite dev server starts
- root route renders

### 3. Axios and query foundation

Proof:

- central client hits a test server successfully
- one normalized error case is proven
- query provider renders successfully

### 4. Playwright bootstrap

Proof:

- one browser smoke test passes
- artifact output works

### 5. Mock daemon harness bootstrap

Proof:

- one daemon-backed project catalog scenario works
- one daemon-backed tree scenario works

### 6. Shell/router/shared primitive scaffold

Proof:

- route shell renders
- shared loading/empty/error/status primitives render
- stable `data-testid` naming exists in at least one route

## Setup Scope

This phase should cover:

- Node package manifests and scripts
- Vite config
- React entrypoint
- central Axios client and interceptor setup
- initial query library setup
- app shell skeleton
- router setup
- basic styling foundation
- spacing tokens and status-badge primitives
- Playwright config
- test fixture scaffolding
- mock daemon environment scaffolding

This phase should not try to complete real website features.

## Suggested Deliverables

### Frontend toolchain

- `package.json` with `dev`, `build`, `preview`, `test` if needed, and Playwright scripts
- Vite config for dev and build
- TypeScript config if TypeScript is chosen
- Axios install and central client wiring
- TanStack Query install and provider wiring if adopted
- lint or formatting config only if it matches repo standards and is worth introducing now

### Frontend communication foundation

- `src/lib/api/client.ts`
- `src/lib/api/errors.ts`
- placeholder feature modules such as:
  - `projects.ts`
  - `topLevelCreation.ts`
  - `tree.ts`
  - `nodes.ts`
  - `prompts.ts`
  - `actions.ts`
  - `sessions.ts`

These modules may begin mostly as stubs, but the ownership split should exist from the start.

### App shell skeleton

- `AppShell`
- `TopBar`
- `ProjectSelectorPage`
- `ExplorerLayout`
- placeholder sidebar tree
- placeholder node detail area
- shared `LoadingState`
- shared `EmptyState`
- shared `ErrorState`
- shared `StatusBadge`

### Router skeleton

At minimum:

- `/projects`
- `/projects/:projectId`
- `/projects/:projectId/nodes/:nodeId`
- `/projects/:projectId/nodes/:nodeId/:tab`

Initial routes may render placeholder content, but the route model should exist from the start.

### Dev-mode integration

The daemon should have a clear future integration path for:

- serving built frontend assets in non-dev mode
- proxying to the Vite dev server in dev mode

The setup phase does not need to finish the production asset serving path, but it should avoid a scaffold that fights that model later.

### Query and invalidation foundation

Phase 1 should also establish:

- shared query provider wiring
- initial query-key conventions
- mutation helper pattern
- placeholder invalidation helpers

The implementation can stay minimal, but the pattern should be present before feature slices begin.

## Playwright Setup Requirements

Phase 1 should install and prove:

- Playwright package and browsers
- base Playwright config
- basic test command
- basic fixture pattern
- artifact output path for screenshots and traces
- stable `data-testid` convention in at least one rendered surface

### Minimum passing test

The minimum browser proof should:

- start the frontend
- open the app
- confirm the shell renders
- confirm a stable hello-world or placeholder marker is visible

This is intentionally trivial.

Its purpose is to prove the browser test stack is alive before feature work begins.

## Mock Daemon Environment Setup

Tests will need deterministic daemon-visible API responses.

Phase 1 should therefore establish a standard strategy for mock environments.

### Recommended direction

Use test fixtures that start a lightweight controlled daemon process or test server surface which serves:

- fixed project lists
- fixed top-level creation responses
- fixed tree payloads
- fixed node detail payloads
- fixed action-catalog payloads

The exact payloads can stay simple in Phase 1.

The important thing is establishing the harness shape early.

### Why this matters

If mock daemon setup is left until late feature work, Playwright coverage will be harder to add and easier to skip.

## Suggested Verification For Phase 1

- frontend package install succeeds
- Vite dev server boots
- app renders basic shell
- Playwright launches successfully
- hello-world browser test passes
- central Axios client can reach the test server successfully

## Suggested Risks

- allowing the scaffold to become a second architecture rather than reflecting the frozen routing note
- adding too much frontend tooling before the app exists
- postponing Playwright until after feature work
- leaving daemon dev-proxy assumptions undocumented
- postponing query/invalidation conventions until after mutations already exist
- postponing shared state primitives until panels already diverge

## Suggested Exit Shape

The setup family is complete when:

- the frontend scaffold exists
- routing skeleton exists
- Playwright exists
- one browser smoke test passes
- mock daemon environment scaffolding exists
- the central client/query foundations exist
- shared state and badge primitives exist in initial form
- later feature work can land into the scaffold without redesigning it first

No setup subphase should be considered complete if it lacks its own proof.
