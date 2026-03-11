# Frontend Website Axios And Query Foundation Decisions

## Purpose

Record the implementation decisions made during web setup phase 02 so later frontend features reuse one stable transport and query foundation.

## Phase-02 Decisions

### Transport layer

The website uses:

- one central Axios client
- one shared error-normalization module

Components should not call Axios directly.

The layering is:

1. central client
2. feature API modules
3. route or panel hooks later
4. presentational components

### Query layer

The website uses:

- TanStack Query

Phase 02 establishes:

- one shared query client
- one shared query provider
- stable query-key helpers

### API-module ownership

The initial module split is:

- `projects.js`
- `topLevelCreation.js`
- `tree.js`
- `nodes.js`
- `workflows.js`
- `prompts.js`
- `actions.js`
- `sessions.js`

This is the frozen ownership baseline for later website routes unless a later note deliberately revisits it.

### Query-key conventions

Phase 02 freezes stable query-key helpers for:

- projects
- project bootstrap
- project tree
- node overview
- node workflow
- node runs
- node prompts
- node summaries
- node sessions
- node provenance
- node actions

### Bounded proof shape

Phase 02 uses one deterministic Node-side proof script that:

- renders the query provider successfully
- proves the central client preserves key defaults
- proves the stable query-key helpers return the expected shapes

This is a bounded setup-phase proof, not a substitute for later browser or daemon-backed tests.
