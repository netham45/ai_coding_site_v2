# Frontend Website UI Communication And Data Access

## Purpose

Define how the website frontend should talk to the daemon and what frontend-side communication conventions should be frozen up front.

This is a working note, not an implementation plan.

## Main Recommendation

Use Axios for HTTP communication with one central configured client instance.

The frontend should not scatter raw `fetch` calls across components.

## Recommended Client Shape

The frontend should have:

- one central Axios instance
- one central auth/session attachment strategy
- one shared error normalization layer
- feature-specific API modules built on top of that client

Suggested structure:

- `src/lib/api/client.ts`
- `src/lib/api/errors.ts`
- `src/lib/api/projects.ts`
- `src/lib/api/topLevelCreation.ts`
- `src/lib/api/tree.ts`
- `src/lib/api/nodes.ts`
- `src/lib/api/prompts.ts`
- `src/lib/api/actions.ts`
- `src/lib/api/sessions.ts`
- `src/lib/api/workflows.ts`
- `src/lib/api/types.ts`

## Axios Client Rules

The central Axios client should define:

- `baseURL`
- auth header behavior
- request timeout policy
- JSON defaults
- common response/error interceptors

### Auth handling

The client should use one central session/auth mechanism.

Likely direction:

- daemon bearer token read from the website-served session/bootstrap context
- Axios attaches it consistently on every request

The frontend should not have each feature manage auth separately.

### Error handling

Axios interceptors should normalize daemon errors into one frontend-friendly shape.

The UI should not parse random backend failures ad hoc in each panel.

## Frontend Data Access Layer

Components should not call Axios directly.

Preferred layering:

1. Axios client
2. feature API modules
3. route/panel loaders or hooks
4. presentational components

Why:

- keeps transport concerns centralized
- makes testing easier
- avoids duplicated request and error logic

## Query State Recommendation

The frontend should also choose a shared strategy for:

- request lifecycle
- caching
- retries
- invalidation after mutations

Recommended direction:

- use a dedicated query/state library rather than handwritten loading state everywhere

Strong candidate:

- TanStack Query

Why:

- route-driven data loading will be common
- post-mutation refresh behavior needs consistency
- tabs and tree/detail panels will need coordinated invalidation

If the project wants to avoid introducing it in setup, that should be a conscious decision rather than an accidental omission.

## Mutation Rules

All frontend mutations should go through shared mutation helpers that define:

- request payload building
- confirmation state integration
- success invalidation
- error handling

This matters especially for:

- top-level creation
- prompt update plus regenerate
- action catalog mutations

## Polling Rules

V1 already prefers polling over websockets.

That means the frontend should also freeze:

- which views poll
- how often they poll
- how polling is paused when a screen is not visible
- which mutations trigger immediate refetch versus waiting for polling

Recommended direction:

- poll only where the operator expects live-ish state
- detail tabs with static history data should not all poll aggressively

## Suggested Frontend Modules To Freeze Early

Beyond Axios itself, the frontend should define these architectural pieces early:

### 1. Route model

Already mostly covered by the routing note, but should stay canonical.

### 2. API module boundaries

Define which modules own:

- projects
- top-level creation
- tree
- node detail
- prompts
- actions
- sessions

Proposed ownership split:

- `projects.ts`
  - project catalog
  - project bootstrap
  - selected project context

- `topLevelCreation.ts`
  - create top-level node
  - creation validation helper shapes

- `tree.ts`
  - expanded tree fetch
  - tree ancestor/sibling helpers if those remain separate

- `nodes.ts`
  - node overview
  - node lineage
  - node versions
  - provenance-oriented summary fetches

- `workflows.ts`
  - current workflow
  - compile detail
  - runs and run progress

- `prompts.ts`
  - prompt history
  - prompt supersede/update mutation
  - regeneration trigger

- `actions.ts`
  - generic action catalog
  - action execution helpers when actions map directly to catalog entries

- `sessions.ts`
  - session list
  - recovery detail
  - attach or resume actions

### 3. Query-key or cache-key conventions

If using a query library, define stable keys for:

- project catalog
- selected tree
- node overview
- node tabs
- action catalog

Proposed query-key shape:

- `["projects"]`
- `["project", projectId, "bootstrap"]`
- `["project", projectId, "tree", rootNodeId]`
- `["node", nodeId, "overview"]`
- `["node", nodeId, "workflow"]`
- `["node", nodeId, "runs"]`
- `["node", nodeId, "prompts"]`
- `["node", nodeId, "summaries"]`
- `["node", nodeId, "sessions"]`
- `["node", nodeId, "provenance"]`
- `["node", nodeId, "actions"]`

Rule:

- every route-owned surface should have one stable query key
- tab-level data should not hide behind one giant catch-all key

### 4. Mutation invalidation rules

Examples:

- top-level creation should invalidate project and tree views
- prompt update plus regenerate should invalidate overview, prompts, actions, and tree
- pause/resume should invalidate overview, runs, actions, and tree

Proposed invalidation table:

- top-level creation
  - invalidate `["projects"]`
  - invalidate `["project", projectId, "bootstrap"]`
  - invalidate `["project", projectId, "tree", rootNodeId]` after route target is known

- prompt update plus regenerate
  - invalidate `["node", nodeId, "overview"]`
  - invalidate `["node", nodeId, "prompts"]`
  - invalidate `["node", nodeId, "workflow"]`
  - invalidate `["node", nodeId, "runs"]`
  - invalidate `["node", nodeId, "actions"]`
  - invalidate affected tree key

- pause or resume
  - invalidate `["node", nodeId, "overview"]`
  - invalidate `["node", nodeId, "runs"]`
  - invalidate `["node", nodeId, "actions"]`
  - invalidate affected tree key

- reconcile children
  - invalidate `["node", nodeId, "overview"]`
  - invalidate `["node", nodeId, "actions"]`
  - invalidate affected tree key

- session attach or resume
  - invalidate `["node", nodeId, "sessions"]`
  - invalidate `["node", nodeId, "actions"]`
  - invalidate `["node", nodeId, "overview"]`

Rule:

- mutations should invalidate the smallest coherent set of affected surfaces
- do not rely only on background polling to reveal mutation results

### 5. Selector and test-id conventions

Playwright will need stable selectors.

Define early:

- `data-testid` strategy
- naming patterns for panels, tabs, buttons, badges, and tree nodes

Proposed format:

- kebab-case
- stable semantic ids, never generated display text
- include entity type when ambiguity is possible

Examples:

- `project-selector`
- `project-option-repo-alpha`
- `top-level-create-form`
- `top-level-create-title`
- `top-level-create-prompt`
- `tree-node-node-100`
- `tree-node-status-node-100`
- `detail-tab-overview`
- `detail-tab-prompts`
- `action-button-regenerate-node`
- `status-badge-blocked`
- `empty-state-prompts`
- `error-state-tree`

Rule:

- test ids belong on stable containers and interaction targets
- do not put Playwright at the mercy of incidental DOM structure

### 6. Loading, empty, and error state patterns

This means defining consistent frontend rendering patterns for:

- loading
- empty data
- daemon/API error

Without this, every panel will improvise.

Proposed shared primitives:

- `LoadingState`
- `EmptyState`
- `ErrorState`

Proposed behavior rules:

- `LoadingState`
  - short label
  - optional skeleton or shimmer for dense panels
  - no spinners as the only indicator on large surfaces

- `EmptyState`
  - clear title
  - one sentence explaining why nothing is shown
  - optional next action when appropriate

- `ErrorState`
  - short explanation
  - normalized daemon error code if available
  - retry action
  - debug expansion for raw error details in debug mode

Examples:

- prompt history empty:
  - title: `No prompt history yet`
  - body: `This node has not recorded any prompt deliveries yet.`

- sessions error:
  - title: `Could not load sessions`
  - body: `The daemon did not return session data for this node.`

### 7. Spacing scale

This means defining one standard padding/margin system such as:

- `4`
- `8`
- `12`
- `16`
- `24`
- `32`

Without this, pages drift visually very quickly.

Proposed spacing tokens:

- `space-1 = 4px`
- `space-2 = 8px`
- `space-3 = 12px`
- `space-4 = 16px`
- `space-5 = 24px`
- `space-6 = 32px`
- `space-7 = 48px`

Proposed usage rules:

- panel internal padding: `space-4`
- dense list row gap: `space-2`
- section gap inside panels: `space-4`
- gap between major panels: `space-5`
- page-shell edge padding: `space-5`

Rule:

- do not introduce one-off spacing values unless a shared token is added deliberately

### 8. Status vocabulary and badge system

Freeze the main vocabulary and color mapping early.

Current proposed direction:

- red: failure/bad
- green: complete/good
- yellow: blocked/caution
- blue: running/in progress
- neutral or white: waiting for user input

Candidate badges include:

- `waiting_user_input`
- `in_progress`
- `waiting_children`
- `reconciliation_failure`
- `compile_failure`
- `blocked`
- `complete`
- `superseded`

Proposed badge vocabulary set for v1:

- `ready`
- `in_progress`
- `waiting_user_input`
- `waiting_children`
- `blocked`
- `compile_failure`
- `reconciliation_failure`
- `paused`
- `complete`
- `superseded`

Proposed mapping direction:

- `ready`
  - neutral or informational
- `in_progress`
  - blue
- `waiting_user_input`
  - neutral or white
- `waiting_children`
  - muted informational
- `blocked`
  - yellow
- `compile_failure`
  - red
- `reconciliation_failure`
  - red
- `paused`
  - yellow or amber
- `complete`
  - green
- `superseded`
  - subdued neutral

Rule:

- badges should express daemon/state vocabulary first, visual flair second

## Polling Proposition

Recommended initial polling schedule:

- tree and node overview
  - every 5 seconds while visible

- runs and sessions
  - every 5 seconds while visible

- prompts, summaries, provenance
  - no automatic polling in v1
  - refetch on tab open and after relevant mutations

Rule:

- pause polling when the browser tab is hidden if the query library supports it cleanly

## Testing Expectations

This communication layer should be tested too.

Expected proof should include:

- bounded tests for API client error normalization
- bounded tests for query invalidation rules
- Playwright proof that core routes survive real request/response flows

## Related Notes

- `2026-03-11_information_architecture_and_routing.md`
- `2026-03-11_ui_consistency_and_design_language.md`
- `2026-03-11_phase_1_setup_and_scaffold.md`
- `2026-03-11_phase_2_feature_implementation.md`
