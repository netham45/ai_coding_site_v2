# Frontend Website UI Top-Level Node Creation Flow

## Purpose

Define the intended v1 operator flow for creating a new top-level node from the website.

This is a working note, not an implementation plan.

## Flow Summary

The website should provide a simple top-level creation screen.

The operator should:

- choose a project from the daemon-exposed `repos/` list
- choose the top-level node kind
- enter the top-level node title
- enter the starting prompt
- confirm creation through an inline footer confirmation state

## Intended Screen Shape

The initial screen can remain deliberately simple.

Required fields:

- project selector
- node kind selector
- title input
- prompt editor

Required actions:

- `Create Node`
- `Keep Editing`

The confirmation UI should be inline rather than modal.

## Field Definitions

### Project

The project field should let the operator choose which source repo directory under `repos/` will be used as the creation source.

The frontend should not scan the filesystem directly.

The daemon should provide the available project list.

### Node kind

The node kind field should initially allow:

- `epic`
- `phase`
- `plan`
- `task`

This should be a bounded selector, not free text.

### Title

The operator should enter the title explicitly for the top-level node.

This should not be silently derived only from the prompt.

The title gives the new root node an operator-chosen identity immediately, before deeper workflow compilation or later summaries exist.

Current backend constraint:

- the existing database schema stores hierarchy-node and node-version titles in `String(255)` fields
- if the website keeps the current schema, the practical title limit is 255 characters rather than 2000

V1 should require:

- non-empty title
- trimmed title
- maximum length aligned with the current backend schema unless a migration changes it

### Prompt

The prompt field should capture the starting instruction set for the new top-level node.

This should be a larger editor area rather than a one-line input.

V1 should not impose content-quality rules beyond requiring a non-empty value that the backend will accept.

## Interaction Flow

The intended v1 creation flow is:

1. operator selects a project
2. operator selects node kind
3. operator enters title
4. operator enters prompt
5. operator clicks `Create Node`
6. UI shows inline confirmation with `create node` and `keep editing`
7. if the operator confirms, the daemon creates the top-level node and routes the UI to the new root node
8. if the operator chooses `keep editing`, the UI returns focus to the form without creating anything

## Confirmation Behavior

The confirmation state should:

- stay inline with the form
- avoid modal interruption
- preserve the entered values
- make it obvious which repo, kind, and title are about to be created

The confirmation state should only become available once:

- project is selected
- node kind is selected
- title is present
- prompt is present

## Post-Create Behavior

If creation succeeds, the website should:

- route to the new node detail screen
- auto-open the new root node in the explorer shell
- show the selected project context
- expose the new node through the standard tree/detail layout

Recommended route target:

- `/projects/:projectId/nodes/:nodeId/overview`

## Backend Semantics

The intended backend effect is:

- create a new top-level node
- clone the selected source repo into the top-level worker repo
- create the top-level branch
- compile the node workflow
- make the new root node available for inspection and later child creation

Current caveat:

- top-level workflow start does not currently perform this repo-backed bootstrap automatically
- this flow therefore implies explicit backend work

Current backend sequence before repo bootstrap is added:

- validate top-level kind
- resolve title
- create the manual node
- capture source lineage
- compile the workflow
- transition to `READY` if compile succeeds
- optionally admit and start the first run

## Error Handling

Errors should remain inline and inspectable.

The v1 flow should handle:

- no projects available under `repos/`
- invalid or missing title
- invalid or missing prompt
- repo bootstrap failure
- daemon rejection of the requested top-level kind

## Testing Expectations

This flow should be tested at multiple layers once implemented.

Expected proof includes:

- bounded UI tests for field validation and confirmation behavior
- daemon/API tests for the creation request contract
- Playwright tests for the full browser creation flow against a controlled daemon environment

## Deferred Help Surface

In-browser prompt help should not be a v1 requirement.

Suggested later target:

- v3: dynamic browser help compiled from the available tools and workflow context

That help should align with the broader workflow-overhaul direction rather than inventing a static website-only help system first.

## Related Notes

- `2026-03-11_v1_scope_freeze.md`
- `2026-03-11_information_architecture_and_routing.md`
- `2026-03-11_phase_2_feature_implementation.md`
- `2026-03-11_phase_3_e2e_testing_and_hardening.md`
