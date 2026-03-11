# Frontend Website UI Consistency And Design Language

## Purpose

Define a lightweight but explicit design language for the website before implementation begins.

This note is not about making the UI artistic.

It is about:

- consistency
- legibility
- predictable state rendering
- predictable action rendering
- shared component behavior

This is a working note, not an implementation plan.

## Main Recommendation

The website should adopt a compact design language up front.

It does not need a huge design-system package before coding starts, but it does need explicit rules for:

- spacing
- typography
- panel structure
- state colors
- action emphasis
- empty/loading/error states
- list and table behavior

Without this, pages will drift visually and behaviorally.

## Design Priorities

The design language should optimize for:

- operator clarity
- dense but readable information
- consistency of status semantics
- consistency of action semantics
- hierarchy awareness

It should not optimize first for:

- marketing-site aesthetics
- novelty
- decorative motion
- highly custom one-off layouts per page

## Visual Tone

The UI should feel:

- operational
- structured
- calm
- information-rich
- trustworthy

The UI should avoid feeling:

- toy-like
- overly consumer-app styled
- overly terminal-cosplay styled
- dashboard-noisy

## Layout Language

The page layout should be built from a small number of reusable primitives.

### Primary layout primitives

- page shell
- panel
- tab strip
- list section
- detail card
- toolbar
- confirmation dialog

### Panel rule

Major content should sit inside visibly consistent panels.

Panels should share:

- padding
- border treatment
- title treatment
- internal spacing

### Density rule

The app should aim for medium information density.

It should not feel:

- sparse and wasteful
- crammed and unreadable

## Typography Rules

Typography should be simple and functional.

### Required text roles

- app title
- page title
- panel title
- section heading
- body text
- metadata text
- code or id text

### Typography consistency rule

The same information role should always use the same text treatment.

Examples:

- node titles should always look like node titles
- timestamps should always look like timestamps
- ids and raw values should always look like machine references

## Color Roles

Colors should be semantic, not decorative.

### Required semantic color roles

- neutral
- success
- warning
- danger
- active or in-progress
- paused
- blocked
- informational

### Proposed initial color mapping

- danger
  - failures
  - compile failures
  - reconciliation failures

- success
  - complete
  - healthy finished states

- warning
  - blocked
  - paused
  - cautionary operator attention

- active
  - running
  - in progress

- neutral
  - waiting for user input
  - superseded
  - inactive metadata

### Color rule

A given state should map to one consistent color role across the app.

For example:

- blocked should not be amber on one page and red on another unless that distinction is formally defined

### Accessibility rule

State meaning should not depend on color alone.

Also use:

- labels
- icons if desired
- consistent badge text

## Status Rendering Rules

Status is one of the most important consistency surfaces.

### Required status surfaces

- lifecycle state
- run state
- blocker state
- session recovery state
- action legality

### Status rendering rule

Every status should render through shared primitives such as:

- `StatusBadge`
- `RollupBadgeGroup`
- `InlineStateLabel`

Do not hand-style statuses independently in each panel.

### Vocabulary rule

Frontend labels should stay aligned with durable backend vocabulary unless a deliberate translation layer is documented.

## Action Rendering Rules

Actions also need a shared language.

### Action levels

Actions should visually distinguish:

- safe routine actions
- caution actions
- destructive actions

### Action consistency rule

The same action risk level should always use the same button emphasis and confirmation behavior.

### Action legality rule

Unavailable actions should not disappear silently unless hiding is intentional and documented.

Default preference:

- show action
- disable it
- show reason

## Surface Types

The app should standardize a few recurring surface types.

### 1. Summary cards

Used for:

- node summary
- run summary
- session summary

Rules:

- compact key facts first
- stable field order
- same spacing and label treatment

### 2. History lists

Used for:

- prompt history
- summary history
- run history
- session event history

Rules:

- chronological ordering rule must be consistent
- selected row state must be consistent
- expandable detail behavior must be consistent

### 3. Structured detail grids

Used for:

- metadata-heavy views
- ids
- timestamps
- version references

Rules:

- stable label/value layout
- easy copyability
- consistent empty-value handling

### 4. Raw JSON surfaces

Used for:

- debugging
- parity checks
- low-level inspection

Rules:

- monospaced
- collapsible if needed
- clearly secondary to structured presentation

## Empty, Loading, And Error States

These must be explicit and consistent.

### Empty state rule

Every major panel should have a defined empty state.

Examples:

- no summaries yet
- no prompt history yet
- no active session

### Loading state rule

Loading should not jump layout wildly.

Use consistent loading skeletons or placeholders inside panels.

### Error state rule

Error states should explain:

- what failed
- whether the rest of the page is still usable
- how to retry

## Form Rules

Even with minimal v1 forms, form styling should be consistent.

### Required form primitives

- text area
- text input
- select
- checkbox
- radio group
- form section
- inline validation text

### Prompt editor rule

The prompt editor should be treated as a primary structured surface, not a one-off text area with ad hoc spacing and controls.

### Confirmation dialog rule

The same dialog structure should be reused for:

- prompt update plus regenerate
- pause or resume confirmation
- regeneration confirmation

## Spacing Rules

Spacing should be standardized so the UI does not feel random.

### Required spacing scale

Use a small consistent spacing scale such as:

- tight
- compact
- normal
- large

The exact token names can vary.

### Spacing rule

Similar components should use the same internal spacing.

Do not tweak margins panel by panel unless there is a clear reason.

## Icon And Badge Rules

Icons are optional, but if used they should be systematic.

### Icon rule

Use icons only where they improve scan speed.

Do not require icons to understand state.

### Badge rule

Badges should be used for:

- status
- kind
- counts
- risk

Not for decorative clutter.

## Tab Rules

Tabs are central to the node detail experience.

### Tab behavior rule

Every tab strip should behave consistently:

- same visual styling
- same selected state
- same overflow behavior
- same loading behavior

### Tab naming rule

Tab names should be short and durable.

Prefer:

- Overview
- Workflow
- Runs
- Prompts
- Summaries
- Sessions
- Provenance
- Actions

## Component Consistency Rules

The app should declare a small set of reusable UI primitives and reuse them aggressively.

### Shared primitives that should exist early

- `Panel`
- `StatusBadge`
- `KeyValueGrid`
- `SectionHeader`
- `EmptyState`
- `LoadingState`
- `ErrorState`
- `ActionButton`
- `ConfirmationDialog`
- `JsonViewer`

### Reuse rule

If two places show the same concept, they should use the same primitive unless a real difference is intentional.

## Interaction Consistency Rules

Behavioral consistency matters as much as visual consistency.

### Rule 1

Selecting a node always updates the main content area in the same way.

### Rule 2

Primary actions always appear in the same region of the screen.

### Rule 3

Mutation results always render through the same feedback pattern.

### Rule 4

Disabled actions always explain why they are unavailable.

### Rule 5

Destructive or high-risk actions always require explicit confirmation.

## Minimal Design Tokens To Define Early

The implementation should likely define at least:

- spacing tokens
- surface colors
- text colors
- semantic status colors
- border radius
- border color
- shadow rules if any
- typography scale

This does not require a full enterprise design system.

It does require discipline.

## V1 Specific Design Language Rules

These rules matter specifically for the first release.

### V1 rule 1

Structured views come before raw JSON views.

### V1 rule 2

The tree is readable first, fancy second.

### V1 rule 3

The prompts tab must feel safe and intentional, not like editing random backend text.

### V1 rule 4

Every status shown in the tree should visually match the status shown in the detail panels.

### V1 rule 5

The app should feel like one coherent operator tool, not a set of disconnected admin pages.

## Open Design Questions

### Question 1

Should the v1 look favor a lighter console-like style or a more document-oriented pane style?

### Question 2

Should raw JSON live in its own tab, or inside each panel as a collapsible subsection?

### Question 3

How visually strong should blocked or failed states be in the tree without making the whole UI feel alarm-heavy?

## V2 Editor Surface Note

If the website later exposes an embedded code-server or in-browser VS Code surface, that editor should be treated as a distinct product surface.

### Design rule

The embedded editor should not break the main website design language, but it also should not force the main operator UI to imitate an IDE.

### Consistency implication

The operator shell should remain:

- orchestration-first
- status-first
- navigation-first

The editor surface should be an intentional secondary environment, not the default design reference for the whole website.
