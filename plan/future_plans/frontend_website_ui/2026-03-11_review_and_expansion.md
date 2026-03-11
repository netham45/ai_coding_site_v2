# Frontend Website UI Review And Expansion

## Purpose

Review the original frontend website UI idea against the repository's current architecture and expand it into a sharper future direction.

This is a working note, not an implementation plan.

### Purpose of this revision

This revision expands the note substantially so it can act as a serious design exploration artifact rather than a short critique.

It also records one concrete narrowing decision:

- full CLI parity is not a v1 requirement

## Architectural Fit

The main direction is sound.

The repository already says:

- the daemon is the live orchestration authority
- the database is the durable canonical record
- CLI and future web clients should talk to the daemon API rather than coordinate directly through the database

That means a browser UI is a natural fit, but only if it is treated as:

- a daemon-served client
- a richer operator surface over the existing authority model
- a consumer of the same durable reads and safe mutation paths the CLI uses

The browser should not grow hidden orchestration rules of its own.

### Architectural conclusion

The strongest overall shape is:

- FastAPI daemon remains the single authority and API host
- React/Vite provides the browser operator experience
- the browser consumes daemon-owned read models and daemon-owned action catalogs
- the browser remains a client, not a second orchestration brain

### Current daemon-surface reality

Reviewing the implemented daemon routes shows that much of the read surface the website needs already exists.

Current daemon routes already cover most of:

- node summary
- tree inspection
- workflow inspection
- prompt history
- summary history
- run progress
- session and recovery visibility
- audit-style deep inspection
- regeneration
- child reconciliation

So the frontend plan should prefer:

- reusing current daemon payloads where they already fit
- expanding backend schemas only where the existing payloads are missing critical UI fields
- avoiding a parallel browser-only API unless the current daemon responses are clearly insufficient

## Product Intent

The UI is not just "a prettier CLI."

It exists to solve a different operator problem:

- reduce cognitive load when navigating large trees
- make state and history visible without dumping raw JSON by default
- surface safe actions in context
- make blocked, paused, failed, and waiting states easier to diagnose
- improve discoverability of features that the CLI already exposes awkwardly

### Product boundary

The UI should not try to replace every CLI use case immediately.

The CLI will still remain stronger for:

- scripting
- batch operations
- automation
- debugging obscure edge cases
- fallback access when the browser UI is unavailable

### Product success criteria

A successful first UI should let an operator:

- find the correct project quickly
- understand the tree state quickly
- understand why a node is blocked or active quickly
- inspect history and artifacts without guessing commands
- perform a small number of safe actions with confidence

## Main Critiques

### 1. "Expose all CLI functionality" is the right aspiration but the wrong first milestone

The current CLI surface is broad and audit-heavy.

A first website release should likely target a narrower slice:

- project selection
- tree and node detail inspection
- run, blocker, and pause-state inspection
- prompt and summary history inspection
- a small set of high-confidence mutations

Trying to ship full CLI parity immediately will probably delay the UI and muddy the API design.

#### Why this matters

If v1 aims at full parity, the team will end up designing:

- too many endpoints at once
- too many destructive-action flows at once
- too many UI states at once
- too little polish in the views operators will actually use first

#### Revised v1 statement

V1 should target:

- high-value read surfaces
- a small bounded mutation set
- strong inspectability
- strong testability

V1 should explicitly defer full CLI parity.

### 2. The tree view needs a summary model and a detail model

The requested tree is rich, but if every node in a large subtree loads:

- full compiled workflow
- every workflow-stage result
- AI summaries
- timestamps
- child status rollups

then the page will become slow quickly.

A better split is:

- tree payload: identity, hierarchy, current lifecycle, current run state, blocker classification, aggregate child rollups
- detail payload: compiled workflow, prompt and summary history, attempt history, session state, artifacts, provenance, and action affordances

#### Tree-summary contract

The tree payload should be optimized for scanning and navigation, not exhaustive inspection.

It should likely include:

- node identity
- title
- kind
- parent identity
- depth
- authoritative version identity
- lifecycle state
- current run state
- blocker classification
- child status rollups
- whether more detail is available on demand

#### Node-detail contract

The detail payload should be optimized for one selected node.

It should likely include:

- canonical summary facts
- active run facts
- compiled workflow metadata
- stage-by-stage result summaries
- prompt history references
- summary history references
- session state and recovery information
- provenance and artifact references
- action catalog

#### Loading model

The browser should support:

- shallow initial tree fetch
- lazy child expansion
- on-demand node-detail fetch
- on-demand tab fetches for heavy data

This avoids turning the UI into one giant overfetching payload.

#### Current implementation comparison

The current daemon tree route already returns a flattened subtree with:

- node id
- parent node id
- depth
- kind
- tier
- title
- lifecycle state
- run status
- scheduling status
- blocker count

What it does not yet include is much of the richer operator data the UI wants at a glance, such as:

- authoritative version id
- child rollup breakdowns
- child count
- timestamps

That is a real backend gap worth tracking explicitly.

### 3. Programmatic selectors require canonical enumerations, not ad hoc UI knowledge

Your instinct to avoid free-text entry is correct.

The missing design detail is that the daemon should expose canonical "available options" endpoints for things like:

- projects
- valid node targets
- available actions for the current node state
- allowed prompt packs or prompt update targets
- valid rerun or reset scopes
- valid intervention types

Otherwise the browser will end up hardcoding rules the daemon already owns.

#### Selector categories

The daemon should expose explicit option surfaces for:

- project selection
- node targeting
- allowed child scopes
- prompt update targets
- workflow profile selections when applicable
- intervention resolution choices
- session recovery choices

#### Why enumerations matter

Enumerated choices reduce:

- invalid operator input
- frontend duplication of business logic
- drift between CLI and web behavior
- accidental exposure of illegal actions

#### Suggested rule

If the browser wants a dropdown, checkbox list, segmented control, or radio group, the daemon should ideally be able to describe that option set directly.

#### Current implementation comparison

The current daemon already exposes many concrete node and session surfaces, so most selectors are not greenfield.

The clearest missing selector surface is project selection itself.

Right now the daemon exposes bootstrap, foundation, and status information, but not a first-class project catalog for git repos or clone bases.

Current direction:

- add a daemon-managed configured repo list
- treat project selection as repo selection, not as a frontend-derived concept

### 4. The action surface should be state-derived, not button-derived

Operations like:

- `git revert`
- prompt replacement
- erase-and-rerun children

should not simply exist as static buttons.

The daemon should return:

- whether the action is currently legal
- why it is legal or blocked
- what confirmation text or preview is required
- what durable audit record will be written
- what follow-up state transitions should be expected

This keeps the UI aligned with the daemon authority model and the automation doctrine.

#### Action catalog concept

The system likely needs a browser-oriented action catalog response for each node or run context.

Each action row should be able to describe:

- stable action id
- display label
- current legality
- illegal reason if blocked
- risk classification
- target scope
- preview data
- confirmation requirements
- expected durable effects
- expected follow-up refresh targets

#### Action grouping

Actions should likely be grouped by operator intent:

- execution control
- recovery
- child management
- review or intervention handling
- history or provenance utilities
- destructive repository mutations

#### Action design principle

The UI should never decide legality from local heuristics like:

- "button enabled because node looks ready"
- "show rerun because lifecycle state equals X"

The daemon should say what is legal.

#### Current implementation comparison

The daemon already has many concrete mutation endpoints for pause, resume, sessions, reconciliation, and regeneration.

What it does not yet appear to expose is a generic browser-oriented action catalog that answers:

- what actions are legal now
- what actions are blocked now
- why they are blocked
- what confirmation text the UI should display

### 5. Website is now a sixth first-class system and the wording should stay disciplined

The repo's core implementation model now names six systems:

- database
- CLI
- daemon
- YAML
- prompts

That change makes sense, but only if responsibilities stay distinct:

- CLI remains the scriptable/operator automation surface
- website becomes the visual operator surface
- daemon remains the authority behind both

This doctrine change now needs explicit updates to:

- system coverage rules
- checklist schemas
- feature inventory
- testing requirements
- observability expectations

#### Why the wording matters

If the website becomes first-class without clear boundaries, the repo could drift into:

- duplicating CLI responsibilities
- hiding logic in frontend code
- claiming feature coverage without browser tests
- forgetting to update doctrine and checklists when UI-impacting changes land

#### Recommended role split

The cleanest split is:

- database: durable record
- daemon: authority and API assembly
- CLI: scriptable and automation-oriented client
- website: visual operator client
- YAML: declarative policy and structure
- prompts: AI-facing behavior assets

#### Doctrine impact

If this change is adopted later, the repository will need:

- checklist schema updates for website status
- testing doctrine updates for browser E2E
- feature-plan scope updates where website behavior is affected
- explicit statements about when a feature does or does not affect the website

### 6. The HTML-form side-task should not start as arbitrary prompt HTML

The right shape is probably structured intervention or input schemas served by the daemon, then rendered by the web client.

For example:

- `type: text`
- `type: textarea`
- `type: boolean`
- `type: enum`
- `type: multi_select`
- validation rules
- help text
- required versus optional

That keeps prompts first-class while avoiding unsafe raw-HTML injection or prompt-specific frontend hacks.

#### Better conceptual model

The daemon should expose a structured input-request contract rather than raw HTML blobs.

That contract can describe:

- field type
- field id
- display label
- help text
- requiredness
- default value
- allowed values
- validation rules
- submission target

#### Likely first use cases

This would be useful for:

- human approval gates
- clarification prompts
- operator intervention decisions
- structured recovery choices
- bounded parameter entry for safe mutations

#### Prompt relationship

Prompts can still define why input is needed and how it is used.

The browser-specific rendering should come from structured metadata, not hand-authored HTML inside prompts.

## Scope Decision

The first concrete scope decision for this future direction is now:

- do not require full CLI parity for v1

### What v1 should optimize for

V1 should optimize for:

- navigation clarity
- state visibility
- operator confidence
- safe action discovery
- rigorous testability

### What v1 should not optimize for

V1 should not optimize for:

- exhaustive mutation coverage
- every obscure maintenance action
- raw power-user scripting parity
- replacing the CLI as the universal tool

## Recommended Future Slices

### Slice 1: Read-only operator dashboard

Start with:

- project selector
- subtree explorer
- node summary panel
- run, blocker, pause, and lineage summaries
- prompt and summary history views
- session and recovery visibility

This delivers value quickly and exercises the read-model design without immediately exposing dangerous mutations.

#### Slice 1 concrete tabs

The initial detail view could plausibly include:

- overview
- workflow
- run state
- prompts
- summaries
- sessions
- provenance

#### Slice 1 explicit non-goals

Slice 1 should probably exclude:

- destructive mutations
- prompt replacement
- git-affecting actions
- child erasure
- arbitrary form authoring

### Slice 2: Safe bounded mutations

Add a small mutation set with durable previews and confirmations:

- pause or resume
- start run
- update the selected node prompt
- reconcile children
- regenerate or rectify
- attach or resume session

These already fit the daemon-owned action model better than low-level git operations.

#### Slice 2 action qualities

Slice 2 actions should have:

- low ambiguity
- clear current legality
- clear confirmation text
- clear durable effects
- low repository-damage risk

#### Slice 2 likely exclusions

Even at this stage, avoid:

- irreversible destructive actions
- broad descendant resets without preview
- anything that can silently invalidate audit expectations

### Slice 3: High-risk destructive or repository-mutating actions

Only after the prior slices are stable:

- revert flows
- prompt replacement
- child erasure
- rerun cascades
- cutover-sensitive operations

These need especially strong audit, confirmation, and E2E coverage.

#### Slice 3 design burden

These actions require more than just a button and a POST endpoint.

They likely need:

- preview of affected scope
- preview of irreversible consequences
- stronger confirmation flows
- richer audit records
- stronger rollback or recovery guidance

## V2 Expansion Ideas

The following ideas fit naturally as post-v1 website expansions.

### Browser-hosted editor access

A strong v2 candidate is:

- open a code-server or in-browser VS Code session rooted at a selected node's working directory

This should be treated as:

- operator-only
- node-scoped
- daemon-coordinated

The operator value is straightforward:

- inspect generated or modified files in the exact node workspace
- perform deeper diagnosis without leaving the browser experience
- move from orchestration state to code state quickly

The main design questions for this later feature are:

- how a node's working directory is resolved and validated
- whether the editor session is ephemeral or reusable
- how auth is handled between daemon and code-server
- whether access is read-only, read-write, or role-dependent
- how this interacts with active sessions already bound to the same workspace
- what audit trail should exist for launching an editor session

## Information Architecture

The main frontend challenge is not visual styling.

It is organizing high-volume orchestration state into views that remain legible.

### Top-level layout

The default shell should likely include:

- project and environment selector bar
- navigation tree or explorer rail
- main content workspace
- status or diagnostics strip for daemon connectivity and auth state

### Detail organization

The main content area should likely use tabbed or segmented sections so operators can move between:

- current state
- workflow state
- historical attempts
- prompt and summary history
- session and recovery details
- artifacts and provenance
- available actions

### Raw data escape hatch

Even with rich structured views, operators will still need a low-level debug escape hatch.

That likely means:

- raw JSON view
- copyable IDs
- copyable timestamps
- direct artifact paths or references
- explicit version and run identifiers

## UI Model Recommendations

### Navigation model

Use a three-part model instead of making the tree carry every concern:

- top bar: project, run-context, environment, daemon health
- left pane: collapsible hierarchy tree with status rollups
- main pane: node detail tabs such as summary, workflow, runs, prompts, summaries, sessions, provenance, and actions

#### Why this layout is stronger

This avoids forcing operators to choose between:

- seeing the tree
- seeing detail
- understanding current environment context

It also scales better once the detail view becomes complex.

### Tree behavior

Instead of pure scroll-to-zoom alone, support:

- expand and collapse
- jump to parent
- focus on subtree
- breadcrumb path
- search within subtree
- depth filters

Scroll zoom can still exist, but it should not be the only navigation primitive.

#### Expand and collapse

Operators need explicit control over:

- how much of the subtree is visible
- which branch they are focusing on
- which levels are noisy or irrelevant

#### Focus and breadcrumbs

Focus mode plus breadcrumbs will matter because orchestration trees can get deep, and operators need to preserve orientation.

#### Search and filtering

Search and filters will likely be as important as the tree itself.

Useful filters may include:

- lifecycle state
- node kind
- blocked only
- active only
- failed only
- assigned profile or role when those exist

### Status rollups

Higher levels should summarize child state explicitly, for example:

- counts by lifecycle state
- blocked child count
- active child count
- failed child count
- waiting-on-dependency count
- last-updated timestamp

That gives real at-a-glance value without opening every child.

#### Rollup display ideas

Useful compact visuals may include:

- stacked status bars
- count chips
- severity-colored badges
- recency indicators

#### Rollup caution

Rollups should summarize, not editorialize.

They should reflect durable state vocabulary rather than inventing new frontend-only interpretations.

## Data Model Recommendations

The browser likely needs a set of explicit UI-facing read models.

These should be API contracts, but they do not all need to be brand-new daemon families.

Where current daemon responses already carry the required durable data cleanly, the website should reuse them directly or compose them in the frontend.

### Tree node summary model

A tree node summary model likely needs:

- stable node id
- authoritative version id
- title
- kind
- depth
- parent id
- lifecycle status
- run status
- blocker status
- child rollups
- recency metadata

Current backend status:

- partially present
- likely needs schema expansion for richer rollups and recency fields

### Node detail model

A node detail model likely needs:

- identity and lineage summary
- current authoritative and current created version facts
- current run facts
- workflow summary
- stage result summary
- prompt and summary references
- session and recovery state
- provenance and artifact references
- action catalog

Current backend status:

- mostly present, but distributed across existing routes
- action catalog remains a genuine missing backend surface

### Tab-specific heavy models

Large detail tabs should probably load separately.

Examples:

- full compiled workflow
- prompt history list
- summary history list
- session event history
- provenance graph or mappings

## API Recommendations

The browser will likely need daemon routes grouped around:

- project selection and discovery
- hierarchy/tree read models
- node detail read models
- workflow and attempt history
- prompt, summary, and provenance history
- action catalogs with legality and confirmation metadata
- mutation execution endpoints

The important rule is that browser-oriented response shapes can differ from CLI output formatting, but they should be assembled from the same authority-owned concepts and legality checks.

### API family 1: environment and project discovery

These routes should answer:

- which projects are available
- which project is active
- what daemon instance the browser is talking to
- whether auth is valid
- whether the daemon is healthy enough for operator interaction

Current backend status:

- daemon health and runtime context are already present
- project discovery is still missing as a first-class daemon route

Current direction:

- implement project discovery as a daemon-managed configured repo list rather than a loose frontend convention
- for the website, that can be as simple as exposing the available directories under `repos/`
- the frontend should not scan the filesystem directly
- the CLI does not need to share this same UX constraint

### API family 2: hierarchy and navigation

These routes should answer:

- what the tree looks like
- what a node's ancestors and children are
- what the current rollups are
- what branches should be lazily expanded

Current backend status:

- tree, ancestors, children, and siblings already exist
- richer rollups and timestamps still need backend expansion

Current recommendation:

- expand the existing tree route rather than inventing a second browser-only tree endpoint
- the current operator-view loader already joins hierarchy, lifecycle, current-version, and blocker inputs in one place
- the missing browser fields should be added to that existing tree response model

### API family 3: detail and history

These routes should answer:

- what is currently happening at the node
- what happened historically
- what prompts, summaries, sessions, and attempts exist
- what artifacts and provenance records are relevant

Current backend status:

- mostly already present via existing daemon routes

### API family 4: action catalog and mutations

These routes should answer:

- which actions are legal right now
- what confirmations are required
- what mutation payload shape is allowed
- what happened after the action ran

Current backend status:

- mutation endpoints mostly already exist
- generic action-catalog output does not yet exist

Current recommendation:

- keep action legality in Python daemon logic rather than YAML
- model the generic action catalog after the current intervention catalog shape
- let both CLI and website consume the same daemon-side action-evaluation service

Why not YAML:

- legality is heavily runtime-state dependent
- static policy mapping would drift from actual live daemon semantics
- the action surface needs blocked reasons and confirmation metadata that are easiest to compute in daemon code

### API family 5: structured human input

If the form idea is pursued, these routes should answer:

- whether input is currently requested
- what schema the form should render
- what validation rules apply
- where the submission should go

## Action Surface Strategy

The most important mistake to avoid is shipping a pile of buttons before action semantics are clean.

### Action maturity tiers

The action surface should probably be planned in tiers:

- informational actions
- reversible control actions
- bounded coordination actions
- destructive repository actions

### Action-catalog design direction

The best current backend precedent is the intervention catalog.

It already expresses:

- a typed action family
- recommended action
- available actions
- details payloads

The generic browser action catalog should follow the same basic pattern, but at the broader node-operator level.

Suggested action fields:

- `action_id`
- `label`
- `group`
- `legal`
- `blocked_reason`
- `confirmation_mode`
- `confirmation_label`
- `target_scope`
- `details_json`

### Action implementation rubric

Every website action should be planned against the same rubric before it is accepted into scope.

Required rubric fields:

- action id
- operator-facing label
- backend endpoint or command surface it triggers
- required request payload
- legality inputs
- blocked conditions
- blocked reason source
- confirmation behavior
- success refresh scope
- durable inspection surface after execution
- bounded tests required
- Playwright coverage required or not

### Safe-first action candidates

Good early candidates are likely:

- pause
- resume
- start run
- update node prompt
- session attach or resume
- reconcile children
- regenerate where legality is already well-defined

### Deferred high-risk actions

Actions to defer until much later likely include:

- git revert
- erase descendants
- rerun large descendant sets
- merge or cutover sensitive repository actions

Node-level prompt modification should be treated separately from broader prompt-pack or wide-scope prompt-management flows.

A bounded "update the selected node's prompt, then regenerate" flow fits the intended operator model much better than deferring all prompt changes entirely.

The cleaner v1 UX is not "save prompt and maybe do something later."

It is:

- edit prompt
- immediately confirm whether to save and regenerate
- if confirmed, save the prompt change and regenerate
- otherwise discard the unsaved edit

Saved prompt drafts should be treated as a later feature, likely v2 or v3, because draft persistence introduces extra questions around lifetime, ownership, collisions, and auditability.

This also means the frontend probably does not need a brand-new single daemon endpoint just to express "save and regenerate now."

The intended UX can still be modeled as two backend mutations:

- change the node prompt through the existing prompt-changing path
- then run regeneration

Frozen direction:

- use the existing version/supersede semantics
- do not treat prompt update as an in-place destructive overwrite of the current node version
- website-driven prompt update plus regeneration should yield a new node version

Current top-level caveat from backend review:

- top-level workflow creation does not currently clone a repo as part of `workflow start`
- repo bootstrap currently exists as a separate live-git concern

So if the website plan expects top-level parent creation to be repo-backed from the start, that will require explicit backend work and note updates rather than assuming the behavior already exists.

Current top-level workflow behavior from backend review:

- `/api/workflows/start` already exists
- it validates that the kind is parentless
- it resolves title
- it creates the manual node
- it captures source lineage
- it compiles the workflow
- it transitions the node to `READY` if compilation succeeds
- it optionally admits and starts the first run

The missing step is repo-backed bootstrap, not the rest of the top-level creation lifecycle.

### Git workflow clarification from backend review

The existing live-git child flow is closer to the intended model than the first draft of this note stated.

Current alignment:

- child workspaces are cloned from the parent/version repo
- child branches are created within that derived repo context
- merge-up is already modeled as bringing child final results back into the parent repo

Still-missing top-level piece:

- the website flow for starting a top-level parent from a source repo under `repos/`
- the daemon work needed to bind top-level workflow start to that selected source repo
- the later operator flow for merging the top-level parent branch back into the base repo

This means the website plan should not describe the git model as wholly missing.

The more accurate statement is:

- child clone-and-merge-up semantics are already present in the live-git model
- top-level source-repo bootstrap and top-level merge-back still need explicit planning and likely backend work

## Performance And Scalability Concerns

The UI will only be useful if it remains fast on real trees.

### Main performance risks

Likely risks include:

- loading too much detail into the tree
- refetching large payloads too often
- rendering huge expanded hierarchies in the browser
- making every tab dependent on one oversized endpoint

### Likely mitigations

Likely mitigations include:

- lazy loading
- paged histories
- tab-specific data fetches
- virtualization for long lists
- explicit refresh scopes

### Freshness model

The UI will also need a conscious freshness strategy.

Options include:

- manual refresh only
- polling
- server-sent events
- websockets

Polling is probably the simplest first implementation unless the repo later proves a stronger real-time need.

## Dev-Mode Serving Recommendation

Your dev-mode idea is reasonable:

- production-like mode: FastAPI serves built static assets
- development mode: FastAPI proxies `/app` or similar routes to the Vite dev server

That keeps one daemon entrypoint while preserving frontend iteration speed.

The main caution is to keep this from leaking dev-only proxy assumptions into production auth and routing behavior.

### Production serving shape

The clean production shape is likely:

- Vite builds static assets
- FastAPI serves those built assets
- browser API calls go to the same daemon origin

### Development serving shape

The clean development shape is likely:

- Vite dev server owns frontend HMR
- FastAPI proxies a frontend path prefix during development
- auth and API base-path behavior stay as close to production as possible

### Routing caution

The team should avoid:

- path mismatches between dev and prod
- separate auth assumptions in dev
- a frontend build that only works when directly hosted by Vite

## Auth And Security Considerations

The current repo already has a local token posture.

The browser plan needs to stay aligned with that.

### Current alignment

The current likely baseline is:

- daemon owns auth
- daemon creates or loads a local bearer token or cookie-equivalent local secret
- CLI uses that same daemon-owned auth boundary

### Browser questions

The browser plan still needs a later decision on:

- how the token reaches the browser
- whether browser use is same-machine only at first
- whether local cookie storage or header injection is preferred
- what CSRF posture is expected if browser mutations exist

### Practical initial posture

A local-first operator UI can start with a deliberately constrained posture, but it should not silently become a remote-ready UI without explicit design work.

## Testing Direction

The testing bar you want is appropriate, but the wording should be tightened:

- Playwright should own real browser E2E coverage
- backend/API invariants should still be proven at unit, integration, and runtime E2E layers
- screenshot plus AI review should be treated as an additional review aid, not the primary proof of UI correctness

For a future UI system, the likely proving stack is:

- unit tests for UI state logic and rendering boundaries
- API integration tests for browser-oriented daemon responses
- Playwright E2E for real operator flows
- visual regression snapshots for stable surfaces
- optional screenshot-to-AI review for subjective layout or clarity checks

### Testing principle

The browser UI should inherit the repository's existing doctrine:

- bounded proof first
- real end-to-end proof later
- no completion claims without real E2E coverage for the intended scope

### Frontend unit and component tests

These should cover:

- state derivation
- view-state transitions
- action rendering rules
- empty and error states
- tab-loading behavior

### API integration tests

These should cover:

- browser-oriented response contracts
- action-catalog legality logic
- structured input-schema payloads if adopted
- auth failure behavior
- pagination and filtering behavior

### Playwright coverage

Playwright should cover real operator flows such as:

- select a project
- navigate a tree
- inspect a node
- view prompt and summary history
- perform a safe action
- see the resulting durable state update

### Visual checks

Visual checks should likely combine:

- deterministic screenshot baselines where feasible
- AI-assisted screenshot review for subjective clarity or layout regressions

The AI-assisted layer should supplement, not replace, deterministic tests.

## Recommended Invariants For A Future UI Note

If this moves forward, the future authoritative note should define invariants such as:

- the browser never performs direct operational database mutations
- every visible mutation maps to a daemon-owned audited action
- every action button is derived from daemon-declared legality
- tree summaries and detail payloads have separate contracts
- UI labels do not invent state vocabulary that conflicts with durable state vocabulary
- destructive actions always show scope and affected descendants before execution
- browser auth uses the same daemon-owned local token posture unless deliberately revised

### Additional invariants worth adding

The future note should probably also state that:

- every browser view has a recoverable empty or unavailable-state rendering
- tree expansion cannot require loading all descendant detail eagerly
- browser mutations always return a refreshable durable result, not just optimistic local state
- browser terminology for states and actions matches canonical durable vocabulary
- deferred actions remain visibly unavailable rather than half-implemented

## Roadmap Structure

If the idea advances, it should probably be planned as multiple authoritative tasks rather than one giant frontend task.

### Likely planning batches

Useful future task slices could include:

- browser-facing daemon read-model design
- browser-facing action-catalog design
- auth and serving model design
- frontend app scaffolding and route shell
- tree and detail information architecture
- safe mutation flows
- structured human-input schema design
- Playwright and visual-review proving

One additional concrete batch now looks necessary:

- daemon schema-gap closure for project selection, richer tree rollups, and action-catalog payloads

### Why batching matters

This project is too stateful and too doctrine-heavy for a one-shot "build a dashboard" effort.

Breaking it into batches will make it easier to:

- prove each contract
- update notes and doctrine cleanly
- keep API and UI aligned
- avoid silently narrowing the intended behavior

## Suggested Next Questions

- Which exact CLI command families are the first release candidates for browser parity?
- What should the browser's project concept map to in current daemon state?
- Is the initial target operator-facing only, or should AI-session intervention flows be in scope from the start?
- Which actions are allowed in the first release, and which are explicitly deferred?
- Does the tree need real-time updates, polling, or event streaming?
- Should node-detail tabs expose raw JSON alongside structured views for debugging parity?

### Recommended immediate follow-up decisions

The next useful planning decisions are probably:

- define the exact v1 read-only versus mutating boundary
- define exactly which existing daemon responses are reused unchanged and which require backend expansion
- define the first action-catalog contract
- decide whether polling is sufficient for v1
- decide whether AI-session intervention forms are in or out of the initial website scope
