# Frontend Website Shell Router And Shared Primitives Decisions

## Purpose

Record the implementation decisions made during web setup phase 05 so later feature work builds on one stable route shell and primitive vocabulary.

## Phase-05 Decisions

### Route skeleton

The bootstrap route skeleton now includes:

- `/projects`
- `/projects/:projectId`
- `/projects/:projectId/nodes/:nodeId`
- `/projects/:projectId/nodes/:nodeId/:tab`
- `/debug/primitives`

These routes are scaffold placeholders, not final feature-complete screens.

### Shell shape

The bootstrap shell now includes:

- top bar
- sidebar
- main content region

This is the stable shape later feature routes should fill in rather than replace casually.

### Shared primitives

The bootstrap primitive set now includes:

- `LoadingState`
- `EmptyState`
- `ErrorState`
- `StatusBadge`

These are the first shared UI-state components for the website.

### Stable scaffold test ids

Phase 05 freezes stable scaffold test ids including:

- `app-shell`
- `top-bar`
- `shell-sidebar`
- `shell-content`
- page-level route markers
- primitive markers such as `loading-state`, `empty-state`, and `error-state`

### Bounded proof shape

Phase 05 extends the deterministic Node-side proof to verify:

- the projects route renders
- the node tab route renders
- the primitive gallery route renders the shared state primitives

This is still setup-phase proof, not a replacement for later browser and daemon-backed route verification.
