# Frontend Website UI V1 Scope Freeze

## Purpose

Freeze the proposed v1 scope for the future frontend website UI so it can be reviewed concretely instead of remaining an open-ended aspiration.

This is a working note, not an implementation plan.

## Scope-Freeze Summary

V1 is a browser-based operator UI served by the daemon's HTTP layer.

V1 is explicitly not:

- full CLI parity
- a replacement for the CLI
- a full destructive-action surface
- a general-purpose AI-session console

V1 is explicitly intended to deliver:

- project selection
- top-level node creation
- tree-based navigation
- rich node inspection
- prompt and summary visibility
- prompt update for the selected node
- session and recovery visibility
- a small bounded action set

### Scope-freeze revision note

This note has been revised after reviewing the current daemon API.

Important consequence:

- many v1 tabs can reuse current daemon responses directly
- the real backend gaps are narrower than the first draft implied

## V1 User

The primary v1 user is a human operator inspecting and managing orchestrator state.

### In-scope user posture

The v1 user is assumed to:

- be operating locally or in the same trusted environment as the daemon
- need visibility more often than mutation power
- use the website for navigation, diagnosis, and bounded actions
- still rely on the CLI for scripting, edge cases, and deferred operations

### Out-of-scope user posture

V1 is not optimized for:

- remote multi-user operation
- broad admin delegation
- arbitrary automation
- provider-console replacement
- full AI-session workflow control

## V1 Screens

V1 should ship exactly these main screens or screen families.

### 1. Project Selector Screen

Purpose:

- choose the active project or workspace context
- expose daemon health and environment identity before deeper navigation

Required elements:

- project list
- current project indicator
- daemon instance summary
- auth-valid or auth-invalid status
- entry point into the main explorer

Required data:

- available projects
- current project
- daemon version or build identifier when available
- daemon reachability state

Backend status:

- partially missing

What already exists:

- bootstrap and daemon status information
- foundation and resource information

What still appears to be missing:

- a first-class project catalog for git repos or clone bases

Current decision:

- use a daemon-managed configured repo list
- the list should come from the source directory used for clone bases
- a `repos/` directory is an acceptable first expectation if users perform the initial clone themselves
- for the website, the operator flow can be as simple as choosing which directory under `repos/` to start from
- this is a website-specific operator constraint, not a CLI constraint

### 1a. Top-Level Node Creation Screen

Purpose:

- let the operator create a new root workflow from a selected source repo

Required elements:

- project selector
- top-level node kind selector
- title input
- prompt editor
- inline confirmation footer

Required interaction:

- operator enters the title explicitly
- operator enters the prompt explicitly
- UI offers `create node` and `keep editing` in the inline confirmation state
- confirmation should only become available once project, kind, title, and prompt are all present

Current backend constraint:

- current title storage is backed by `String(255)` fields, so v1 should align with that unless the schema is expanded

Backend status:

- partially missing because current top-level workflow start does not yet perform the intended repo-backed bootstrap

### 2. Main Explorer Screen

Purpose:

- provide the default operator workspace
- keep the tree visible while allowing selected-node inspection

Required layout:

- top bar for project and daemon context
- left sidebar tree or hierarchy explorer
- main detail panel for selected node

Required capabilities:

- switch selected node
- preserve selection state
- keep hierarchy context visible while inspecting detail

### 3. Node Detail Tabs

The main detail panel should ship with these tabs.

#### 3a. Overview Tab

Required content:

- node title
- node kind
- logical node id
- authoritative version id
- lifecycle state
- current run state
- blocker status
- parent identity
- child rollup summary
- created and updated timestamps

#### 3b. Workflow Tab

Required content:

- compiled workflow summary
- stage list
- current stage marker
- per-stage outcome summary
- compile status summary

Deferred from this tab in v1:

- full graphical workflow editor
- arbitrary stage mutation controls

#### 3c. Runs Tab

Required content:

- active run summary when present
- recent run history list
- trigger reason
- start and end timestamps
- result summary

#### 3d. Prompts Tab

Required content:

- prompt history list
- prompt type or family labels when available
- prompt timestamps
- delivered prompt detail view
- current editable prompt source for the selected node
- prompt update submission flow for the selected node that leads directly into regeneration confirmation

Deferred from this tab in v1:

- prompt-pack switching
- saved prompt drafts

Backend status:

- prompt history and prompt record lookup already exist
- node-level prompt update exists only indirectly through current prompt-changing node mutations
- the website still needs to choose which existing mutation path becomes the canonical UI flow

#### 3e. Summaries Tab

Required content:

- summary history list
- summary timestamps
- stage association when available
- detail view for one selected summary

#### 3f. Sessions Tab

Required content:

- current primary session state
- recent session history
- recovery classification when available
- recommended action when available
- provider or tmux visibility already exposed by the daemon

#### 3g. Provenance Tab

Required content:

- source lineage summary
- relevant docs or artifact references
- version and run references needed for operator inspection

Deferred from this tab in v1:

- advanced provenance graph visualization
- edit-in-place provenance mutation

#### 3h. Actions Tab

Required content:

- grouped action catalog
- legality state for each action
- blocked reason for illegal actions
- confirmation UI for legal actions
- resulting operation feedback

## V1 Tree Behavior

The tree is a central v1 feature.

It should behave as an operator navigation tool, not as a full detail surface.

### Required tree capabilities

- expand and collapse children
- select a node
- preserve current selection
- show ancestor path or breadcrumb
- show child status rollups
- focus on a subtree

### Required tree filters

- lifecycle state filter
- blocked-only filter
- active-only filter
- kind filter

### Allowed but non-required v1 behavior

- scroll zoom
- keyboard navigation
- saved filters

### Explicitly deferred tree behavior

- freeform drag-and-drop restructuring
- visual layout editing
- full graph-mode layout separate from the hierarchy tree

## V1 Data Surfaces

V1 should consume current daemon responses directly wherever they are already good enough.

Only the missing fields or missing aggregation layers should require backend expansion.

### Required read model 1: app bootstrap

Purpose:

- load project and daemon context for the browser shell

Required fields:

- available_projects
- current_project
- daemon_health
- daemon_identity
- auth_state

Reuse status:

- likely assembled from current bootstrap, foundation, and daemon-status routes
- still needs a project-catalog source

Current decision:

- project catalog should come from a daemon-managed configured repo list rather than filesystem guessing inside the frontend
- for the website, the daemon should expose the available directories under `repos/` as the project-selection source
- the frontend should not scan the filesystem directly

### Required read model 2: tree summary

Purpose:

- populate the left-hand hierarchy explorer

Required fields per node:

- node_id
- authoritative_node_version_id
- latest_created_node_version_id
- title
- kind
- tier
- parent_node_id
- depth
- lifecycle_state
- run_status
- scheduling_status
- blocker_state
- blocker_count
- child_rollups
- has_children
- child_count
- created_at
- last_updated_at

Reuse status:

- current tree route is a good base
- backend expansion is still needed for richer rollups, version ids, child count, and timestamps

Current recommendation:

- expand the existing `/api/nodes/{node_id}/tree` response rather than adding a second route
- the current operator-view loader already assembles most of the underlying data needed for that expansion

### Required read model 3: node overview detail

Purpose:

- populate the overview tab quickly

Required fields:

- node identity block
- parent summary
- authoritative version summary
- current run summary
- child rollup summary
- timestamps
- top-level blocker details

Reuse status:

- likely assembled from existing summary, lineage, lifecycle, blockers, and run routes

### Required read model 4: workflow detail

Purpose:

- populate the workflow tab

Required fields:

- compiled_workflow_id
- compile_status
- current_stage
- stage_summaries
- workflow_version_refs when available

### Required read model 5: run history

Purpose:

- populate the runs tab

Required fields:

- current_run
- recent_runs
- run result summaries

### Required read model 6: prompt history

Purpose:

- populate the prompts tab

Required fields:

- prompt list
- selected prompt detail
- prompt family or type
- delivered timestamp
- current editable prompt payload for the selected node
- prompt update legality metadata

Reuse status:

- history data is already present
- editable prompt source is already present on node or version payloads
- prompt-update legality metadata is not yet a dedicated daemon surface

### Required read model 7: summary history

Purpose:

- populate the summaries tab

Required fields:

- summary list
- selected summary detail
- stage association
- timestamp

### Required read model 8: session and recovery detail

Purpose:

- populate the sessions tab

Required fields:

- current primary session
- session list
- recovery classification
- recommended action
- recent session events if already exposed cleanly

### Required read model 9: provenance summary

Purpose:

- populate the provenance tab

Required fields:

- source lineage summary
- docs or artifact references
- current authoritative references

### Required read model 10: action catalog

Purpose:

- populate the actions tab

Required fields per action:

- action_id
- label
- group
- legal
- blocked_reason
- confirmation_mode
- confirmation_label
- target_scope_summary
- details_json
- mutation_payload_schema when needed

Reuse status:

- not currently present as a generic daemon response
- this remains one of the clearest genuinely new backend payloads

Current recommendation:

- model this after the current intervention catalog style rather than inventing an unrelated shape
- keep legality evaluation in daemon Python code, not YAML policy

## V1 Actions

V1 should ship only a small bounded mutation set.

### Actions explicitly in scope

The current recommended in-scope v1 actions are:

- `pause_run`
- `resume_run`
- `start_run`
- `update_node_prompt`
- `session_attach`
- `session_resume`
- `session_provider_resume`
- `reconcile_children`
- `regenerate_node`

### Action design rubric

Every v1 action should be documented against the same planning rubric before implementation.

Required rubric fields:

- action id
- operator-facing label
- backend endpoint or canonical command surface
- required request payload
- legality inputs
- blocked conditions
- blocked reason source
- confirmation behavior
- success refresh scope
- durable post-action inspection surface
- bounded test coverage
- Playwright coverage

### Why these actions are in scope

These actions are the best fit for v1 because they are:

- operationally meaningful
- already aligned with daemon authority
- easier to explain in UI language
- safer than repository-destructive operations

### Prompt update and regenerate coupling

V1 should treat prompt update and regeneration as a coherent operator flow.

The important product rule is:

- `regenerate_node` without a way to update or replace the node prompt is not sufficient

The website therefore needs to support:

- viewing the current prompt basis for the node
- editing or replacing that prompt input through a daemon-owned mutation
- regenerate confirmation before committing the prompt change

This does not require full prompt-pack management in v1, but it does require node-level prompt modification.

Implementation note:

This is a two-step backend flow, not necessarily one daemon endpoint.

The frontend can support the intended UX by:

- collecting the prompt edit
- asking for save-and-regenerate confirmation
- calling the existing prompt-changing mutation path
- then calling regeneration

Current backend-path options for prompt change before regeneration:

- use the existing node-supersede path with a new prompt
- add a narrower node-prompt-update mutation if implementation proves the supersede path too awkward for the website

Current recommendation:

- treat the existing prompt-changing node-version mutation path as the baseline

Frozen decision:

- updating the prompt and regenerating the node should use the current version/supersede semantics
- the result should be a new node version rather than in-place clobbering of the old node version
- the original node version should remain inspectable and reconstructible

### Prompt update interaction rule

The intended v1 interaction should be:

1. operator edits the node prompt
2. UI asks whether to save and regenerate now
3. operator can confirm regeneration or discard the unsaved changes
4. if the operator confirms, the daemon saves the prompt change and starts regeneration

The core product shape is:

- "save and regenerate now?"
- `[yes]`
- `[discard changes]`
- `[keep editing]`

V1 should not introduce long-lived draft storage for partially edited prompt text.

### Action requirements

Every v1 action must have:

- daemon-declared legality
- daemon-declared blocked reason when unavailable
- explicit confirmation when appropriate
- durable result visible after completion
- clear post-action refresh behavior

### Actions explicitly deferred from v1

These actions should not be in v1:

- `git_revert`
- erase children
- rerun descendants in bulk
- cutover-sensitive merge or finalize actions
- manual tree editing through drag-and-drop or inline creation flows
- top-level merge-back-to-base controls

### Why these actions are deferred

These actions carry too much:

- destructive scope
- audit complexity
- legality ambiguity
- downstream blast radius

for a first website release.

## V1 Response Shapes To Review

These are draft server-to-browser JSON shapes, not user-flow sketches and not final API contracts.

They exist so the scope can be reviewed concretely.

### Important clarification

These draft shapes should now be read as one of two things:

- direct reuse targets for existing daemon responses
- gap sketches for fields the current daemon does not yet expose cleanly enough

### 1. App bootstrap response

```json
{
  "daemon": {
    "identity": "local-dev",
    "healthy": true,
    "auth_state": "valid"
  },
  "projects": [
    {
      "project_id": "project_alpha",
      "label": "project_alpha",
      "selected": true
    }
  ]
}
```

Reality check:

- close in spirit to current bootstrap plus status data
- still missing a real project catalog surface

### 2. Tree summary response

```json
{
  "root_node_id": "node_100",
  "nodes": [
    {
      "node_id": "node_100",
      "authoritative_node_version_id": "nv_100",
      "latest_created_node_version_id": "nv_100",
      "title": "Top Level Epic",
      "kind": "epic",
      "tier": "epic",
      "parent_node_id": null,
      "depth": 0,
      "lifecycle_state": "READY",
      "run_status": "IDLE",
      "scheduling_status": "ready",
      "blocker_state": "none",
      "blocker_count": 0,
      "child_rollups": {
        "active": 1,
        "blocked": 0,
        "failed": 0,
        "waiting": 2
      },
      "has_children": true,
      "child_count": 3,
      "created_at": "2026-03-11T11:00:00Z",
      "last_updated_at": "2026-03-11T12:00:00Z"
    }
  ]
}
```

Reality check:

- partially covered by the current tree route
- richer rollups, timestamps, and version ids remain backend expansion targets
- this should be delivered by expanding the existing tree route rather than inventing a second route

### 3. Node overview response

```json
{
  "node": {
    "node_id": "node_101",
    "node_version_id": "nv_101",
    "title": "Implementation Phase",
    "kind": "phase",
    "lifecycle_state": "RUNNING",
    "run_state": "ACTIVE",
    "blocker_state": "none"
  },
  "parent": {
    "node_id": "node_100",
    "title": "Top Level Epic"
  },
  "rollups": {
    "children_total": 4,
    "active": 1,
    "blocked": 1,
    "failed": 0,
    "waiting": 2
  },
  "timestamps": {
    "created_at": "2026-03-11T11:00:00Z",
    "updated_at": "2026-03-11T12:00:00Z"
  }
}
```

Reality check:

- likely better assembled from current summary, lineage, run, and blocker routes than introduced as a brand-new daemon route immediately

### 4. Action catalog response

```json
{
  "node_id": "node_101",
  "actions": [
    {
      "action_id": "update_node_prompt",
      "label": "Update Prompt",
      "group": "node_configuration",
      "legal": true,
      "blocked_reason": null,
      "confirmation_mode": "inline",
      "confirmation_label": "save and regenerate",
      "target_scope_summary": "Selected node prompt only",
      "details_json": {
        "mutation_path": "/api/nodes/{node_id}/supersede + /api/nodes/{node_id}/regenerate"
      }
    },
    {
      "action_id": "pause_run",
      "label": "Pause Run",
      "group": "execution_control",
      "legal": true,
      "blocked_reason": null,
      "confirmation_mode": "inline",
      "confirmation_label": "pause run",
      "target_scope_summary": "Current run only",
      "details_json": {
        "daemon_path": "/api/nodes/pause"
      }
    },
    {
      "action_id": "regenerate_node",
      "label": "Regenerate Node",
      "group": "child_management",
      "legal": false,
      "blocked_reason": "Node has active child sessions.",
      "confirmation_mode": "inline",
      "confirmation_label": "regenerate node",
      "target_scope_summary": "Selected node and its generated descendants",
      "details_json": {
        "daemon_path": "/api/nodes/{node_id}/regenerate"
      }
    }
  ]
}
```

Reality check:

- still mostly future work because the daemon currently has concrete mutations but not a generic action-catalog response

## V1 Interaction Rules

V1 should follow these exact interaction rules.

### Rule 1

Tree selection changes the main detail panel without navigating away from the explorer shell.

### Rule 2

Heavy tabs should fetch on demand instead of preloading all detail.

### Rule 3

Mutation buttons should come from the action catalog, not from hardcoded frontend assumptions.

### Rule 4

Illegal actions may still be visible, but they must render as unavailable with the daemon-provided reason.

### Rule 5

Every successful mutation should trigger a predictable refresh of:

- current node overview
- tree summary for impacted scope
- action catalog
- the directly impacted tab when relevant

### Rule 6

Project routes should auto-select the root node by default.

## V1 Explicit Deferrals

The following work is explicitly outside v1 and should be reviewed as deferred rather than accidentally implied.

### Deferred feature set

- full CLI parity
- high-risk git operations
- descendant erasure flows
- manual tree editing UI
- workflow authoring UI
- arbitrary form-builder UI
- saved prompt drafts
- in-browser code-server or VS Code access for node working directories
- in-browser dynamic prompt-help guidance
- multi-user auth and authorization model
- rich real-time event streaming if polling is good enough
- advanced graph visualization beyond the hierarchy tree

### Prompt drafts deferral note

Draft persistence for partially edited prompts is worth planning, but it should be treated as a later feature.

Recommended target:

- v2 or v3: saved prompt drafts for node-level edits

That later feature would need decisions about:

- draft scope per node or per user
- draft lifetime
- collision behavior
- draft-to-regeneration workflow
- audit expectations for discarded versus applied drafts

### Dynamic prompt-help deferral note

V1 should not attempt to teach the user how to write prompts through a rich in-browser guidance system.

Recommended target:

- v3: dynamic browser help compiled from available tools and workflow context, aligned with the future workflow-overhaul direction

### Deferred technical questions

- final browser auth transport details
- whether polling or SSE is the long-term update model
- whether AI-session interventions belong in the initial website release

Current direction after review:

- website doctrine updates are now adopted in the repo doctrine
- polling is acceptable for v1
- AI/session interaction through the website is out of v1 scope

## Known Backend Gaps For V1

The current review suggests these are the main backend gaps the website still needs:

- project catalog for git repos or clone bases
- richer tree payload fields:
  - authoritative version id
  - child rollup breakdowns
  - child count
  - timestamps
- generic action catalog with legality and confirmation metadata
- prompt-update legality metadata if the UI is to stay state-derived

This is now the frozen working backend-gap list for the frontend plan.

All four richer tree additions above should be treated as required rather than optional.

Current recommendation:

- implement the richer tree fields by expanding the existing tree route
- implement action legality through a generic daemon-side action catalog service rather than YAML policy

## Later Operator Flow: Merge Top-Level Parent Back To Base Repo

This is intentionally outside v1, but it should be explicit in the future plan because it affects repository-state modeling and later action design.

### Intended outcome

After a top-level parent node has incorporated child work, the operator should eventually be able to merge the top-level parent branch back into the selected source repo from `repos/`.

### Proposed later UI flow

- operator starts from the root node or project-level action area
- UI shows the selected base repo, the top-level parent branch, and the base branch target
- UI shows whether child merge-up is complete
- UI shows whether the parent workspace is legally ready for merge-back
- operator can inspect a merge-back preview or summary
- operator confirms merge-back only when daemon legality checks pass
- UI surfaces success or failure as an inspectable durable event

### Placement rule

This should be treated as a project-level or root-node-level action surface, not a generic action on arbitrary descendant nodes.

### Backend implication

The daemon will need an explicit top-level merge-back surface and legality model for this later flow.

## Explicit V2 Candidate

One explicit v2 website feature worth planning now is:

- launch a code-server or in-browser VS Code session in the selected node's working directory

This is intentionally out of v1 because it adds new concerns around:

- workspace resolution
- editor-session lifecycle
- auth and embedding
- read-write safety
- interaction with active node sessions

## V1 Acceptance Checklist For Review

These are the exact questions this scope-freeze note is meant to answer.

### Review question 1

Are these the correct v1 screens?

### Review question 2

Are these the correct in-scope actions?

### Review question 3

Are the deferred actions and features correctly deferred?

### Review question 4

Are these data surfaces sufficient for the screens without overscoping v1?

### Review question 5

Are these draft server JSON shapes close enough to the information the daemon should provide?

### Review question 6

Should structured human-input forms be part of v1 or explicitly moved to v2?

### Review question 7

Is the proposed prompt-update flow sufficient for v1, or does it need a stronger coupled UX that immediately leads from prompt change into regeneration?

### Review question 8

Should saved prompt drafts be planned explicitly for v2 or v3 as a separate feature family?

### Review question 9

Are the identified backend gaps the right ones, or is there another missing daemon field family the website will obviously need?

## Recommended Next Authoritative Planning Slices

If this scope freeze is accepted, the next likely planning slices are:

- browser-facing daemon read-model task plan
- browser-facing action-catalog task plan
- frontend app shell and route structure task plan
- Playwright browser E2E planning note
