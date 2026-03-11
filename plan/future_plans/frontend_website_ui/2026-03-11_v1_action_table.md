# Frontend Website UI V1 Action Table

## Purpose

Freeze the proposed v1 action table so the website action surface is planned concretely rather than abstractly.

This is a working note, not an implementation plan.

## Action Table

### `pause_run`

- Label: `Pause Run`
- Backend surface: `/api/nodes/pause`
- Scope: current node run
- Legal when:
  - node has an active pausable run
- Blocked when:
  - no active run exists
  - run is already paused
  - lifecycle state does not allow pause
- Confirmation:
  - inline
  - label: `pause run`
- Success refresh:
  - overview
  - runs
  - actions
  - affected tree
- Required proof:
  - daemon/API legality test
  - UI rendering test
  - Playwright action-flow test

### `resume_run`

- Label: `Resume Run`
- Backend surface: `/api/nodes/resume`
- Scope: current node run
- Legal when:
  - node is resumable
  - paused state allows resume
- Blocked when:
  - node is not paused
  - resume gate not satisfied
- Confirmation:
  - inline
  - label: `resume run`
- Success refresh:
  - overview
  - runs
  - actions
  - affected tree
- Required proof:
  - daemon/API legality test
  - UI rendering test
  - Playwright action-flow test

### `start_run`

- Label: `Start Run`
- Backend surface:
  - existing run-admission/start surface used by daemon/CLI
- Scope: selected node
- Legal when:
  - node is compiled and ready
  - no conflicting active run exists
- Blocked when:
  - compile failed
  - dependency blockers exist
  - active run already exists
- Confirmation:
  - inline
  - label: `start run`
- Success refresh:
  - overview
  - runs
  - actions
  - affected tree
- Required proof:
  - daemon/API legality test
  - UI rendering test
  - Playwright action-flow test

### `update_node_prompt`

- Label: `Update Prompt`
- Backend surface:
  - `/api/nodes/{node_id}/supersede`
  - followed by regeneration flow
- Scope: selected node prompt
- Legal when:
  - node can be superseded
  - prompt editing is allowed for the selected node
- Blocked when:
  - node state forbids supersession/regeneration
  - conflicting active state prevents prompt replacement flow
- Confirmation:
  - inline editor footer
  - label: `save and regenerate`
- Success refresh:
  - overview
  - prompts
  - workflow
  - runs
  - actions
  - affected tree
- Required proof:
  - prompt-flow mutation tests
  - UI editor tests
  - Playwright prompt-flow test

### `session_attach`

- Label: `Attach Session`
- Backend surface:
  - session attach/recovery daemon surface
- Scope: selected node session
- Legal when:
  - attachable session exists
- Blocked when:
  - no attachable session exists
  - session backend denies attach
- Confirmation:
  - usually none or low-friction inline
- Success refresh:
  - sessions
  - overview
  - actions
- Required proof:
  - daemon/API session legality test
  - UI rendering test

### `session_resume`

- Label: `Resume Session`
- Backend surface:
  - session recovery action surface
- Scope: selected node session
- Legal when:
  - resumable session recovery status exists
- Blocked when:
  - recovery classification does not allow resume
- Confirmation:
  - inline
  - label: `resume session`
- Success refresh:
  - sessions
  - overview
  - actions
- Required proof:
  - daemon/API recovery-action test
  - UI rendering test

### `session_provider_resume`

- Label: `Provider Resume`
- Backend surface:
  - provider session recovery action surface
- Scope: selected node session/provider binding
- Legal when:
  - provider-backed rebind or resume is possible
- Blocked when:
  - provider not supported
  - provider session missing
  - daemon recovery status forbids it
- Confirmation:
  - inline
  - label: `resume provider session`
- Success refresh:
  - sessions
  - overview
  - actions
- Required proof:
  - daemon/API provider-recovery test
  - UI rendering test

### `reconcile_children`

- Label: `Reconcile Children`
- Backend surface:
  - child reconciliation daemon surface
- Scope: selected node child authority state
- Legal when:
  - reconciliation is required
  - daemon exposes available decisions
- Blocked when:
  - no reconciliation is pending
  - node has no reconciliation decision available
- Confirmation:
  - inline
  - label depends on selected decision
- Success refresh:
  - overview
  - actions
  - affected tree
- Required proof:
  - daemon/API reconciliation test
  - UI decision rendering test
  - Playwright action-flow test

### `regenerate_node`

- Label: `Regenerate Node`
- Backend surface:
  - `/api/nodes/{node_id}/regenerate`
- Scope: selected node and its generated descendants
- Legal when:
  - daemon considers regeneration safe
  - conflicting child/session state does not block it
- Blocked when:
  - active child sessions exist
  - lifecycle or authority mode forbids it
- Confirmation:
  - inline
  - label: `regenerate node`
- Success refresh:
  - overview
  - workflow
  - runs
  - actions
  - affected tree
- Required proof:
  - daemon/API regeneration legality test
  - UI blocked-reason test
  - Playwright regenerate-flow test

## Table Rule

Every action above should eventually be converted into an implementation rubric/checklist entry before coding begins.
