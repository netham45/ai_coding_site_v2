# Frontend Website Action Surface Decisions

## Context

This note records the implementation decisions for the website bounded action-surface phase.

## Decisions

### The daemon owns legality

The website should not infer action legality from ad hoc frontend state.

The daemon now exposes `GET /api/nodes/{node_id}/actions`, and that response is the browser authority for:

- which actions exist for the selected node
- whether each action is legal
- why a blocked action is blocked
- which confirmation label should be shown inline

### The first-pass catalog reuses existing daemon helpers

The first-pass action catalog is derived from existing runtime helpers rather than a new YAML policy table.

The legality evaluation reuses:

- node operator summary
- pause state
- session recovery status
- provider recovery status
- child reconciliation inspection
- rebuild coordination inspection

### The browser still calls concrete daemon endpoints

The generic catalog does not imply a generic browser execute endpoint in v1.

The website action tab renders the daemon catalog, but action execution still calls the existing concrete daemon endpoints, including:

- `/api/node-runs/start`
- `/api/nodes/pause`
- `/api/nodes/resume`
- `/api/sessions/attach`
- `/api/sessions/resume`
- `/api/sessions/provider-resume`
- `/api/nodes/{node_id}/children/reconcile`
- `/api/nodes/{node_id}/regenerate`

This keeps the action surface aligned with the existing daemon and CLI command analogs while still centralizing legality in the daemon.

### Reconciliation decisions are exposed as concrete action ids

Child reconciliation is represented as action ids of the form:

- `reconcile_children:<decision>`

This keeps the daemon action response explicit without forcing the browser to invent decision names.

### The first pass is intentionally bounded

The v1 action catalog exposes the approved bounded action family only.

It does not yet replace:

- interventions
- prompt editing flow
- broader git conflict workflows
- future higher-risk bulk operations

### Refresh stays targeted

After a successful action mutation, the website invalidates:

- the current node query family
- the current project query family

The browser stays on the `actions` tab and shows a small local success state for the action that was just executed.
