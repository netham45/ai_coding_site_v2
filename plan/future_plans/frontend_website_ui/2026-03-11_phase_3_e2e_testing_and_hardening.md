# Frontend Website UI Verification Family

## Purpose

Define the verification-family phases that turn the implemented website from "features exist" into "the browser flow is actually proven."

This is a working note, not an implementation plan.

## Family Goal

Use Playwright and controlled daemon environments to prove the website end to end across the main operator journeys, blocked/error journeys, and route-refresh behavior.

This family should also explicitly audit for missing tests and untested flows rather than assuming implementation batches covered everything correctly.

## Core Rule

This phase is not optional polish.

It is the proving layer that makes browser-side completion claims defensible.

## Test Environment Strategy

The website tests need daemon-visible environments that are deterministic and easy to start.

### Recommended approach

Create test harnesses that can launch the daemon against controlled mock environments whose API-visible state represents specific operator scenarios.

Those scenarios should include:

- empty project catalog
- top-level creation success
- top-level creation validation failure
- one project with a small healthy tree
- large tree with mixed child states
- blocked node
- active run
- failed run
- prompt history present
- sessions needing inspection
- action catalog with both legal and illegal actions

### Why mock environments matter

The browser UI should be tested against scenarios that are:

- stable
- reproducible
- fast enough for repeated Playwright runs

The daemon still needs to be the process presenting those scenarios over HTTP.

## Verification Family Breakdown

The verification work should be broken into at least these phases:

1. route and happy-path E2E proof
2. blocked/error/recovery E2E proof
3. visual-review artifact proof
4. missing-test and untested-flow audit

## Required E2E Flow Families

### Flow family 1: app bootstrap and project selection

Must prove:

- app loads
- project list renders
- project selection works
- top-level creation form works
- title entry is required for creation
- prompt entry is required for creation
- successful creation redirects to the new root node
- root node auto-selection works
- refresh preserves route state

### Flow family 2: tree navigation

Must prove:

- tree renders
- node selection updates URL
- back/forward navigation works
- filters work
- hierarchy context remains visible
- expanded tree fields render correctly in the sidebar

### Flow family 3: detail tab navigation

Must prove:

- tabs are route-driven
- deep links open the correct tab
- refresh preserves the correct tab
- loading and empty states behave correctly

### Flow family 4: prompt edit and regenerate

Must prove:

- prompt history is visible
- prompt edit path works
- keep-editing works
- discard works
- confirm save-and-regenerate works
- resulting version transition is reflected correctly

### Flow family 5: bounded actions

Must prove:

- legal actions are invokable
- illegal actions render with reasons
- confirmation flows work
- UI refreshes predictably after action completion
- action buttons remain targetable through stable `data-testid` conventions

### Flow family 6: blocked and failure inspection

Must prove:

- blocked states are visible in both tree and detail surfaces
- failed states are inspectable
- operator can understand why a node is blocked or failed

## Visual Review Strategy

Playwright can assert many things, but not all visual quality questions.

The E2E phase should therefore also define:

- stable screenshot capture points
- artifact retention for review
- when screenshot diffs are enough
- when screenshots should be passed to an AI review step for visual sanity checking

### Candidate screenshot targets

- project selector
- top-level creation form
- explorer shell with mixed-state tree
- detail overview tab
- prompt editor footer confirmation state
- blocked-node action panel

## Adversarial And Recovery Flows

This phase should not stop at the happy path.

It should also cover:

- daemon unavailable at load
- invalid or expired auth
- empty or missing project catalog
- missing node after deep link
- action rejected by daemon
- stale data refresh after route load

## Untested-Flow Audit Requirement

The final verification pass should explicitly answer:

- which routes exist
- which views exist
- which shared component families exist
- which actions exist
- which of those have bounded tests
- which of those have Playwright coverage
- which flows remain untested

The desired outcome is not vague confidence.

The desired outcome is an explicit "no known untested v1 flows remain" conclusion, or a documented list of residual gaps.

## Suggested Verification For Phase 3

- Playwright suite passes for core route flows
- Playwright suite passes for prompt-edit flow
- Playwright suite passes for blocked and error flows
- screenshot artifacts are generated for visual-review targets
- core tested surfaces use the frozen semantic `data-testid` conventions

## Suggested Risks

- trying to rely on component tests instead of browser-route proof
- building brittle Playwright tests against unstable selectors
- testing only happy-path payloads
- not freezing deterministic mock scenarios
- treating visual review as optional for the more diagrammatic screens
- letting stable selector or badge vocabulary drift after tests are written

## Suggested Exit Shape

The verification family is complete when:

- the browser app is covered by meaningful Playwright flows
- deterministic daemon-backed mock environments exist for test scenarios
- route, refresh, and interaction flows are proven
- visual-review support exists for areas raw assertions cannot judge well
- the tested flows reflect the frozen contracts and frontend conventions rather than one-off test-only behavior
- missing-test and untested-flow audit has been performed explicitly
