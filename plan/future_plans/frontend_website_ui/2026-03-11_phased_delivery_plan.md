# Frontend Website UI Phased Delivery Plan

## Purpose

Propose a practical delivery split for the website work so implementation can be staged cleanly instead of opened as one oversized batch.

This is a working note, not an implementation plan.

## Delivery Structure

The website effort should be divided into many smaller phases, not three oversized buckets.

The old three-note split is still useful, but only as phase families:

- setup family
- feature family
- verification family

The actual proposed execution sequence should be much more granular.

## Proposed Granular Phase Sequence

### Phase 0: Node And Repo Runtime Baseline

Goal:

- confirm Node is usable in this repo
- define frontend working directory and package boundary
- define canonical frontend commands

Must include tests or proof:

- version check
- package install proof
- one documented command surface

### Phase 1: Vite And React Bootstrap

Goal:

- create the Vite/React app
- prove it boots
- prove the route shell can render

Must include tests or proof:

- app boots
- placeholder shell renders

### Phase 2: Axios And Query Foundation

Goal:

- add the central Axios client
- add feature API-module skeletons
- add query/cache provider and initial conventions

Must include tests or proof:

- central client reaches a test server
- normalized error handling works
- query provider wiring works

### Phase 3: Playwright Bootstrap

Goal:

- install Playwright
- create base config
- prove a trivial browser test

Must include tests or proof:

- one passing hello-world browser test
- trace and screenshot artifact paths are working

### Phase 4: Mock Daemon Harness

Goal:

- create deterministic daemon-presented test scenarios
- define how browser tests boot those scenarios

Must include tests or proof:

- one daemon-backed scenario for project list
- one daemon-backed scenario for tree data
- one daemon-backed scenario for action catalog data

### Phase 5: Shell, Router, And Shared UI Primitives

Goal:

- build the stable app shell
- build the route skeleton
- build shared primitives like loading, empty, error, status badge

Must include tests or proof:

- route rendering tests
- shared-state primitive rendering tests
- one Playwright route-smoke test beyond hello-world

### Phase 6: Feature Plan Family Kickoff

Goal:

- begin feature implementation using the stronger category-level feature plans rather than one plan per tiny component

Primary feature-plan units:

- project bootstrap and selection
- explorer shell and hierarchy tree contract
- detail tabs
- prompts and regeneration flow
- bounded action surface

Route/view/component coverage should live inside those plans rather than replacing them.

### Phase 7: Project Selector View

Goal:

- implement project selector UI
- implement project catalog wiring
- implement project-route entry behavior

Must include tests or proof:

- project list rendering
- empty-state rendering
- selection behavior
- refresh-safe route behavior

### Phase 8: Top-Level Creation View

Goal:

- implement the top-level creation screen
- implement the project-scoped creation contract
- prove title/prompt/kind/project validation and redirect behavior

Must include tests or proof:

- form validation tests
- backend contract tests
- Playwright creation-flow tests

### Phase 9: Expanded Tree Contract

Goal:

- expand the existing tree route
- expose authoritative/latest version ids, rollups, counts, timestamps

Must include tests or proof:

- daemon/API tests for expanded tree payload
- browser rendering tests for expanded tree data

### Phase 10: Tree Sidebar View

Goal:

- implement the actual hierarchy tree UI
- wire selection, filters, status rollups, and URL synchronization

Must include tests or proof:

- filter tests
- selection tests
- route-sync tests
- Playwright tree navigation tests

### Phase 11: Overview Tab

Goal:

- implement the overview tab
- render node identity, lifecycle, run summary, child rollups, timestamps

Must include tests or proof:

- overview rendering tests
- empty/loading/error tests

### Phase 12: Workflow Tab

Goal:

- implement the workflow tab
- render compile status and stage summaries

Must include tests or proof:

- workflow rendering tests
- route-tab tests

### Phase 13: Runs Tab

Goal:

- implement the runs tab
- render active run and history

Must include tests or proof:

- runs history rendering tests
- refresh and polling tests

### Phase 14: Prompts Tab And Regenerate Flow

Goal:

- implement prompt history
- implement prompt editing
- implement supersede plus regenerate flow

Must include tests or proof:

- prompt history tests
- keep-editing/discard/confirm tests
- backend mutation-flow tests
- Playwright prompt-edit flow tests

### Phase 15: Summaries Tab

Goal:

- implement summary-history UI

Must include tests or proof:

- summary list/detail rendering tests

### Phase 16: Sessions Tab

Goal:

- implement sessions and recovery UI

Must include tests or proof:

- session list tests
- recovery state tests

### Phase 17: Provenance Tab

Goal:

- implement provenance/source-lineage view

Must include tests or proof:

- provenance rendering tests

### Phase 18: Actions Tab And Generic Action Catalog

Goal:

- implement grouped action UI
- implement generic action catalog backend surface
- apply the action rubric to every in-scope action

Must include tests or proof:

- legality rendering tests
- blocked-reason tests
- confirmation tests
- backend catalog tests

### Phase 19: Shared Design Consistency Pass

Goal:

- enforce badge vocabulary
- enforce spacing tokens
- enforce shared loading/empty/error treatment
- enforce stable `data-testid` usage

Must include tests or proof:

- component-level consistency tests where useful
- Playwright selector sanity checks
- screenshot review targets updated

### Phase 20: Flow Audit And Missing-Test Sweep

Goal:

- verify every implemented route, panel, component family, and action has tests
- identify any untested or weakly tested flows

Must include tests or proof:

- explicit feature-to-test mapping review
- list of missing tests reduced to zero or documented deferrals

### Phase 21: Final E2E Verification And Hardening

Goal:

- run the full Playwright narrative set
- verify blocked/error/recovery flows
- verify screenshots and visual review targets

Must include tests or proof:

- final browser-route proof
- adversarial-flow proof
- visual review artifacts

## Phase Families

The detailed family notes remain useful, but they should now be read as collections of the granular phases above rather than the full delivery split by themselves.

Detailed notes:

- `2026-03-11_phase_1_setup_and_scaffold.md`
- `2026-03-11_phase_2_feature_implementation.md`
- `2026-03-11_phase_3_e2e_testing_and_hardening.md`

## Cross-Phase Rules

These rules should hold across all granular phases.

### Rule 1

The browser remains a daemon client, not a second orchestration authority.

### Rule 2

Every meaningful feature lands with tests in the same phase that introduces it.

### Rule 3

Playwright should be introduced in setup, used during feature work, and become mandatory in the E2E phase.

### Rule 4

Browser tests should run against controlled daemon environments rather than fragile hand-built operator state.

### Rule 5

Mock daemon environments are acceptable for frontend-focused proving, but the final phase should still exercise the real daemon server process and real browser behavior.

### Rule 6

Frontend transport, query, invalidation, badge, spacing, and shared-state primitives should be frozen early and reused rather than improvised per feature slice.

## Suggested Sequencing

Suggested execution order:

1. finish the setup family first
2. land feature phases in small route/view/component batches
3. treat the final verification family as a real audit and proof sweep, not a formality

## Suggested Phase Boundaries

The important boundary is no longer "did one of three giant phases finish?"

The important boundary is:

- did the specific granular phase land
- did it land with tests
- did it leave any newly introduced untested flows behind

## Completion Standard For This Plan

The proposed delivery split should be considered mature only if:

- every setup concern has an explicit proof step
- every major route/view has its own implementation phase
- every major shared component family has proof obligations
- the final verification family explicitly audits for missing tests and untested flows

## Deferred Beyond These Phases

These phases should not imply immediate delivery of:

- multi-user auth expansion
- websocket or SSE live updates
- browser-hosted code-server integration
- top-level merge-back to base repo
- saved prompt drafts

Those remain later work even if the initial three phases succeed.
