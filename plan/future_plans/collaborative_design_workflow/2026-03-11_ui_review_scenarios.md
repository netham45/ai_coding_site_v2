# UI Review Scenarios

## Purpose

Define a future reusable concept for getting a running application into a specific reviewable UI state without repeating the same setup and click-through work every time.

This is a working note.

## Core Recommendation

The collaborative-design workflow should eventually rely on reusable `ui_review_scenario` definitions.

A review scenario should describe:

- what UI state is being reviewed
- how to reach it
- which runtime mode to use
- which artifacts should be captured

## Why Scenarios Matter

Many useful review targets are not directly openable.

Examples:

- an admin page behind login and several navigation steps
- a checkout state with specific cart contents
- an account page that depends on seeded profile state
- a modal only visible after certain actions

Without scenarios, every design pass wastes time recreating that path manually.

## Scenario Strategies

The future system should support several ways to reach a review state.

### 1. Direct URL

Best when the page is directly routable.

Use when:

- the page is addressable by URL
- only minimal app state is required

### 2. Seeded State

Use a real local backend plus deterministic fixture data.

Use when:

- the page depends on specific records
- realism matters
- the review should stay close to production behavior

### 3. Auth Injection

Use a known local auth state or test identity.

Use when:

- login is not the design target
- repeated auth steps add no value

### 4. Scenario Route Or Debug Entry

Open a dev-only route that materializes a specific state quickly.

Use when:

- the page takes many steps to reach
- local-only review speed matters more than perfectly realistic navigation

### 5. Playwright Navigation

Automate the real UI steps needed to reach the target.

Use when:

- the navigation path itself matters
- state cannot be cleanly materialized another way

### 6. Mocked API State

Run the real frontend against deterministic mocked responses.

Use when:

- the design review is primarily visual or structural
- backend complexity would slow iteration

## Draft Scenario Shape

```yaml
kind: ui_review_scenario
id: account_settings_default
target:
  type: page
  route: /settings/account
runtime_contract_ref: web_app_local_dev
mode: fixture_seeded
auth:
  strategy: local_test_user
state_entry:
  strategy: direct_url
  url: http://127.0.0.1:3000/settings/account
seed:
  command: pnpm scenario:seed account-settings-default
artifacts:
  capture:
    - screenshot_desktop
    - screenshot_mobile
    - browser_console
    - network_failures
```

## Required Scenario Fields

Likely required concepts:

- target surface
- runtime contract reference
- state-entry strategy
- auth strategy
- seed or mock requirements
- expected review artifacts

## Scenario Selection Policy

The system should prefer the cheapest strategy that still gives trustworthy review value.

A likely order is:

1. direct URL with real state
2. seeded real backend state
3. scenario route or auth injection
4. Playwright navigation
5. mocked API state

That order may change depending on what is being tested.

## Realism Versus Speed

Not every review pass needs full realism.

A likely lifecycle is:

- early review: seeded or mocked state for fast iteration
- late review: real backend and real navigation where flow fidelity matters

## Recommended Next Step

Pair this with a note that explains how Playwright and mock layers should cooperate instead of competing.
