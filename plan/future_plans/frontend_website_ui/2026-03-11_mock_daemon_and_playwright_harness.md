# Frontend Website UI Mock Daemon And Playwright Harness

## Purpose

Freeze the recommended browser-test harness shape before implementation begins.

This is a working note, not an implementation plan.

## Recommendation

Use a real daemon process in a deterministic test mode or deterministic seeded scenario mode.

Do not treat frontend-only API stubs as the main proving surface.

## Desired Testing Shape

Browser tests should run against:

- real browser
- real frontend app
- real daemon HTTP process
- deterministic scenario data presented by the daemon

## Recommended Harness Design

### Core idea

The daemon should be startable in a test scenario mode where it serves controlled project/tree/node/action states over the normal API surface.

The frontend should not know whether the daemon is serving live orchestration data or a frozen scenario.

### Why this is the right compromise

This gives:

- realistic HTTP behavior
- realistic auth behavior
- realistic response-model use
- deterministic Playwright scenarios

Without forcing every browser test to create full live orchestration state from scratch.

## Suggested Scenario Families

Minimum useful scenarios:

- empty project catalog
- project selector with one repo
- top-level creation success
- top-level creation validation failure
- small healthy tree
- mixed-state tree
- blocked node
- failed node
- prompt-history-rich node
- session-recovery node
- action catalog with legal and illegal actions

## Harness Layers

### Layer 1: scenario definition

Define scenario data in one structured place.

Suggested shape:

- scenario id
- project catalog payload
- tree payload
- node detail payloads
- action catalog payloads
- mutation responses

### Layer 2: daemon test-mode loader

The daemon test mode should load one named scenario and expose the normal routes from that scenario.

### Layer 3: Playwright fixtures

Playwright should start:

- the daemon in a chosen scenario
- the frontend app
- then navigate with stable URLs

## What Not To Do

Avoid:

- frontend-only mocked `fetch`/Axios interception as the main proof
- brittle per-test JSON injection in the browser
- separate fake API contracts that drift from daemon models

Those are acceptable for narrow bounded frontend tests, but not as the primary E2E story.

## Mutation Testing Direction

Mutation-capable scenarios should support:

- fixed legal action responses
- fixed blocked action responses
- deterministic post-mutation refresh state

This is important for:

- top-level creation
- prompt update plus regenerate
- pause/resume
- reconciliation actions

## Verification Expectations

The harness is good enough when:

- scenarios are cheap to boot
- scenario names are stable
- Playwright can choose scenarios directly
- scenario responses use daemon-owned models
- mutation flows can be tested without ad hoc browser patching

## Recommendation Summary

Preferred choice:

- real daemon process with deterministic scenario mode

Acceptable fallback:

- daemon started against seeded deterministic fixtures that produce the same effect

Least preferred primary path:

- frontend-only API mocking
