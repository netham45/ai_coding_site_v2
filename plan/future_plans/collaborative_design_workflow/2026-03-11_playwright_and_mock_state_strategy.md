# Playwright And Mock State Strategy

## Purpose

Clarify how browser automation, mocked data, seeded data, and real runtime behavior should work together for collaborative design review.

This is a working note.

## Core Recommendation

Playwright should probably be the main automation backbone for reaching and capturing UI review states.

But Playwright alone is not the whole answer.

The future system should support multiple backing-state modes:

- real backend
- fixture-seeded backend
- mocked backend responses
- route interception
- dev-only scenario routes

## Why Playwright Is Still Useful

Playwright helps with:

- opening a real browser
- reproducing navigation reliably
- capturing screenshots
- capturing traces and console output
- verifying that a state is actually reachable

It is a strong default for “get me to the page and show me what changed.”

## Why Playwright Alone Is Not Enough

If every review requires Playwright to click through a long flow from scratch, the loop becomes slow and fragile.

That is exactly the tedium this future feature should remove.

So the stronger design is:

- use Playwright as the driver
- but let scenarios shortcut state entry when appropriate

## Recommended Modes

### Mode 1: Real Navigation, Real Backend

Use when:

- final confidence matters
- the navigation path is itself under review
- interactions across pages matter

Strength:

- highest realism

Weakness:

- slowest

### Mode 2: Direct Open, Seeded Real Backend

Use when:

- the page is directly routable
- realistic data matters
- repeated review speed is important

Strength:

- strong realism with less setup friction

Weakness:

- requires deterministic seed tooling

### Mode 3: Direct Open, Mocked Backend

Use when:

- visual review matters more than backend behavior
- edge states are hard to synthesize in the real backend

Strength:

- fastest iteration

Weakness:

- can drift away from true backend contracts

### Mode 4: Dev-Only Scenario Route

Use when:

- a complex UI state is otherwise tedious to reach
- the route can be kept explicitly local or debug-only

Strength:

- very fast repeated review

Weakness:

- requires careful discipline so debug-only behavior does not leak into production assumptions

## Browser-Level Mocking Options

A normal local consumer browser is enough for realistic local review.

Possible strategies later include:

- local mock API server
- service-worker-based mocking
- Playwright request interception
- fixture-backed local backend
- local cookies or storage injection for auth state

Nothing about this requires a special browser.

The important part is deterministic local control over state.

## Artifact Capture

Playwright-backed review runs should probably capture:

- desktop screenshot
- mobile screenshot
- current URL
- console errors
- failed network calls
- trace when the path is long or flaky

These artifacts should be durable enough that the operator and AI can refer back to them during revision rounds.

## When Mocking Is Acceptable

Mocking is acceptable when the goal is:

- fast design iteration
- layout review
- empty/loading/error state review
- edge-state exploration

Mocking is weaker when the goal is:

- proving the real backend contract
- proving cross-page flow behavior
- proving final release confidence

## Recommended Next Step

The next useful companion note would be a response-shape draft for reporting scenario status, captured artifacts, and review readiness to the CLI and future browser UI.
