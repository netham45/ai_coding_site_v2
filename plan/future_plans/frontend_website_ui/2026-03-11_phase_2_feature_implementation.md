# Frontend Website UI Feature Family

## Purpose

Define how the frozen v1 website scope should be implemented once the frontend scaffold exists.

This is a working note, not an implementation plan.

## Family Goal

Implement the v1 operator UI and the required daemon/browser support surfaces in bounded slices, with tests landing alongside each feature.

This phase should build on the frozen frontend foundations rather than redefining transport, query, spacing, badge, or test-id conventions inside each slice.

## Core Rule

No feature should be considered landed in this phase unless it includes tests.

That includes:

- frontend component tests or equivalent bounded UI proof where appropriate
- daemon/API tests for new or expanded browser-facing surfaces
- Playwright coverage when the feature introduces a meaningful route or interaction that benefits from browser proof

## Recommended Feature Plans

The higher-level feature categories should remain the main proposed feature-plan units.

Those stronger categories are:

1. project bootstrap and selection
2. explorer shell and hierarchy tree contract
3. detail tabs
4. prompts and regeneration flow
5. bounded action surface

These should be treated as the primary future feature plans.

## Route/View/Component Coverage Inside Each Feature Plan

The more granular route/view/component work should live inside those feature plans as implementation coverage, not as a replacement for them.

Examples:

- project bootstrap and selection should cover:
  - project selector route
  - top-level creation view
  - root-node redirect behavior

- explorer shell and hierarchy tree contract should cover:
  - expanded tree contract
  - tree sidebar view
  - filters
  - route synchronization

- detail tabs should cover:
  - overview tab
  - workflow tab
  - runs tab
  - summaries tab
  - sessions tab
  - provenance tab

- prompts and regeneration flow should cover:
  - prompt history
  - prompt editor
  - inline confirmation state
  - supersede plus regenerate behavior

- bounded action surface should cover:
  - action catalog
  - action panel
  - legality rendering
  - blocked reasons
  - confirmations

### Feature Plan 1: project bootstrap and selection

Should deliver:

- project selector page
- top-level node creation screen
- daemon-backed project catalog from `repos/`
- project-scoped top-level creation contract implementation
- project route entry
- root-node auto-selection behavior
- explicit top-level title entry
- top-level prompt entry and confirmation flow

Tests should cover:

- project list rendering
- project selection and route update
- top-level creation form rendering
- title-required validation
- create-node confirmation flow
- success redirect to the new root node
- empty project list state
- daemon/API response handling

### Feature Plan 2: explorer shell and hierarchy tree contract

Should deliver:

- persistent shell
- sidebar tree
- lazy expansion behavior if used
- required filters
- selected-node synchronization with route
- expanded tree contract implementation

Backend work likely needed:

- richer tree payload fields:
  - authoritative version id
  - latest created version id
  - child rollup breakdowns
  - child count
  - created timestamp
  - last updated timestamp
  - blocker state
  - blocker count

Current direction:

- implement these fields by expanding the existing tree route rather than adding a second tree endpoint

Tests should cover:

- tree rendering
- selection behavior
- route reload behavior
- filter behavior
- blocked and active rollup visibility
- correct rendering of version-aware tree status

### Feature Plan 3: overview, workflow, runs, summaries, sessions, provenance tabs

This umbrella should still be split further during implementation task planning.

Minimum expectation:

- do not land all tabs as one untested bundle
- each tab should have its own tests and review surface

Should deliver:

- detail tab layout
- tab routing
- overview panel
- workflow panel
- runs panel
- summaries panel
- sessions panel
- provenance panel
- per-panel debug JSON toggle

Tests should cover:

- tab switching
- on-demand data loading
- loading, empty, and error states
- raw JSON toggle behavior

### Feature Plan 4: prompts and regeneration flow

Should deliver:

- prompt history panel
- prompt editor
- inline footer confirmation state
- `yes`, `discard changes`, and `keep editing` flow
- version/supersede-backed prompt update plus regenerate behavior

Tests should cover:

- prompt history rendering
- editing state
- keep-editing behavior
- discard behavior
- confirm-and-regenerate behavior
- post-action refresh

### Feature Plan 5: bounded action surface

Should deliver:

- action panel
- grouped action catalog
- legal versus illegal rendering
- daemon-provided blocked reasons
- confirmation behavior for bounded actions
- action design rubric applied per action

Backend work likely needed:

- generic action catalog endpoint or equivalent browser-facing legality surface

Each action should be implemented against a shared rubric that records:

- backend endpoint or command surface
- legality inputs
- blocked conditions
- confirmation behavior
- refresh behavior
- bounded tests
- Playwright coverage

Tests should cover:

- legal action rendering
- disabled/blocked action rendering
- confirmation behavior
- refresh after action execution

## Required Backend Work During This Phase

The feature phase is not frontend-only.

It should also deliver the missing backend surfaces the browser needs:

- project catalog from `repos/`
- richer tree payload fields
- generic action catalog or equivalent legality model
- any missing prompt-update legality metadata

Current direction:

- expand the existing tree route instead of adding a second tree endpoint
- keep action legality in daemon Python logic rather than YAML mapping
- use the frozen frontend API-module, query-key, invalidation, and `data-testid` conventions instead of per-slice improvisation

## Route/View/Component Rule

Every major route, view, or shared component family should have explicit implementation and proof planning.

Examples:

- project selector route
- top-level creation form
- tree node card
- overview panel
- prompt editor
- action panel
- loading/empty/error primitives

Do not hide large amounts of work inside one vague feature-plan item.

But also do not explode every component into its own top-level feature plan if it naturally belongs inside one of the stronger categories above.

## Required Testing Rule

Every feature slice above should land with proof in the same slice.

That means:

- no "tests later" feature merges
- no relying only on manual browser checks
- no deferring browser-route proof until after all screens exist

## Suggested Verification For Phase 2

At the end of the feature family, the repo should have:

- passing frontend bounded tests
- passing daemon/API tests for browser-facing additions
- passing targeted Playwright tests for implemented routes and core flows
- implemented query invalidation behavior matching the frozen mutation rules
- implemented shared loading, empty, and error primitives across the major panels

## Suggested Risks

- overbuilding UI before the daemon contracts are stable
- hardcoding action logic in the frontend
- building tree and detail views against invented payloads instead of current daemon surfaces
- letting the prompt-edit flow drift away from version/supersede semantics
- skipping tests for "just UI" changes
- allowing test-id naming or status badge vocabulary to drift by feature

## Suggested Exit Shape

The feature family is complete when:

- the frozen v1 screens exist
- the frozen v1 bounded actions exist
- the browser uses daemon-derived read and legality surfaces
- each implemented feature has tests
- the top-level creation contract and expanded tree contract are reflected in the shipped browser behavior
- the app is ready for full E2E and adversarial browser proof

No route or major panel should remain only manually tested.
