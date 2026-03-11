# CLI API And Inspection Surfaces

## Purpose

Map the collaborative-design concept onto likely future CLI and daemon surfaces so the idea stays inspectable and operational rather than prompt-only.

This is a working draft.

## Design Rule

Every meaningful review state or design artifact should be inspectable from real surfaces.

## Likely Read Surfaces

### CLI

Possible future commands:

- `design status --node <id>`
- `design requirements --node <id>`
- `design rules --node <id>`
- `design overrides --node <id>`
- `design review-rounds --node <id>`
- `design verification --node <id>`

### Daemon

Possible future routes:

- `GET /api/nodes/{node_id}/design-status`
- `GET /api/nodes/{node_id}/design-requirements`
- `GET /api/nodes/{node_id}/design-rules`
- `GET /api/nodes/{node_id}/design-overrides`
- `GET /api/nodes/{node_id}/design-verification`

## Likely Mutation Surfaces

### CLI

Possible future commands:

- `design submit-review --node <id>`
- `design confirm-requirements --node <id>`
- `design request-revision --node <id>`
- `design approve --node <id>`
- `design stop --node <id>`
- `design escalate --node <id>`

### Daemon

Possible future routes:

- `POST /api/nodes/{node_id}/design-review`
- `POST /api/nodes/{node_id}/design-requirements/confirm`
- `POST /api/nodes/{node_id}/design-revision-request`
- `POST /api/nodes/{node_id}/design-approval`
- `POST /api/nodes/{node_id}/design-stop`
- `POST /api/nodes/{node_id}/design-escalation`

## Required Response Concepts

The inspection surfaces should probably expose:

- current review state
- current round number
- effective workflow profile
- effective design rule set
- current requirement capture
- approved overrides
- pending human action
- latest verification results

## Why This Matters

Without dedicated surfaces, collaborative design would be hard to:

- resume after interruption
- audit
- automate
- inspect during failure
- integrate into a future browser UI

## Relationship To Workflow Overhaul

These surfaces are a specialization of the same broader inspectability model already implied by workflow-overhaul:

- profile-aware execution
- persisted artifacts
- runtime-visible obligations
- operator-facing inspection

## Recommended Next Step

If this becomes more concrete later, the next useful note would be a draft response-shape document parallel to the workflow-overhaul API response note.
