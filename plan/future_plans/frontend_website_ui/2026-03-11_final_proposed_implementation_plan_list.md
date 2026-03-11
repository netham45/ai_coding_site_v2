# Frontend Website UI Final Proposed Implementation Plan List

## Purpose

Freeze the final proposed implementation-plan list that should be opened when the website effort moves from future planning into authoritative execution planning.

This is a working note, not an implementation plan.

## Plan List

The proposed implementation plans should be:

1. frontend runtime and toolchain setup family
2. frontend communication and state foundation
3. Playwright and mock-daemon harness setup
4. project bootstrap and selection
5. explorer shell and hierarchy tree contract
6. detail tabs
7. prompts and regeneration flow
8. bounded action surface
9. verification and missing-test audit

## Plan 1: frontend runtime and toolchain setup family

Scope:

- Node/package baseline
- Vite/React bootstrap
- dev/proxy fit
- shell/router/shared primitive scaffold

Required proof:

- package install
- app boot
- route shell render

## Plan 2: frontend communication and state foundation

Scope:

- central Axios client
- API module skeleton
- query/cache layer
- invalidation conventions
- stable `data-testid` conventions

Required proof:

- client integration tests
- query/invalidation tests

## Plan 3: Playwright and mock-daemon harness setup

Scope:

- Playwright bootstrap
- artifact paths
- deterministic daemon-presented scenarios

Required proof:

- hello-world browser test
- scenario-backed browser test

## Plan 4: project bootstrap and selection

Scope:

- project selector
- project catalog from `repos/`
- top-level creation flow
- project-scoped top-level creation contract
- root-node redirect behavior

Nested coverage expected:

- project route
- creation view
- creation validation

Required proof:

- UI tests
- daemon/API contract tests
- Playwright creation flow

## Plan 5: explorer shell and hierarchy tree contract

Scope:

- persistent explorer shell
- expanded tree route
- tree sidebar
- filters
- route synchronization

Nested coverage expected:

- shell layout
- tree node rendering
- tree status rollups
- tree selection behavior

Required proof:

- daemon/API tree tests
- frontend tree tests
- Playwright tree navigation

## Plan 6: detail tabs

Scope:

- overview
- workflow
- runs
- summaries
- sessions
- provenance

Nested coverage expected:

- one implementation slice per tab or tightly related tab subgroup
- shared loading/empty/error and debug JSON behavior

Required proof:

- per-tab rendering tests
- route/tab tests
- Playwright deep-link coverage for meaningful tabs

## Plan 7: prompts and regeneration flow

Scope:

- prompt history
- prompt editor
- inline confirmation
- supersede plus regenerate

Required proof:

- bounded prompt-edit tests
- backend mutation-flow tests
- Playwright prompt flow

## Plan 8: bounded action surface

Scope:

- generic action catalog
- action panel
- legality rendering
- blocked reasons
- confirmations

Required proof:

- daemon action-catalog tests
- per-action rubric coverage
- Playwright action-flow tests

## Plan 9: verification and missing-test audit

Scope:

- final Playwright narrative set
- blocked/error/recovery proof
- visual-review artifacts
- missing-test sweep
- untested-flow audit

Required proof:

- explicit coverage checklist
- final E2E runs
- residual-gap list if anything remains deferred

## Rule For This Plan List

These are the recommended top-level implementation-plan units.

They are intentionally stronger categories than:

- one plan per component
- one plan per tiny panel

But they still require route/view/component-level implementation and tests inside each plan.
