# Frontend Website UI Original Starting Idea

## Purpose

Preserve the original starting idea for a future frontend website UI before it is refined into authoritative implementation plans.

This is a working note, not an implementation plan.

## Original Starting Idea

- Toolkit: `node` + `vite` + `react`
- Purpose: allow the user to navigate and manipulate the state of the engine through a web interface and take advantage of the browser's ability to present data more cleanly and visually than a CLI dumping JSON.
- The daemon is already HTTP-based, so the website should run off the same HTTP layer.
- The daemon itself should serve the website.
- If dev mode is active, the daemon should proxy website traffic through to the Vite dev server.
- The website should expose all functionality the CLI has.
- The website should query available features through HTTP endpoints and present them in user-friendly lists.
- The UI should not rely on the user to enter values as free text when the available values can be determined programmatically.
- The UI should have a project selector.
- The UI should have a list selector that moves from `epic -> phase -> plan -> task -> subtasks`.
- All subtasks should be visible with full detail.
- Higher levels should show the stage or status of their children at a glance.
- The UI should include a tree view.
- The tree should start at the parent node, list phases smaller below, list plans smaller below, tasks below that, and subtasks below the tasks.
- The user should be able to zoom in or out on any point by scrolling.
- Clicking an element should bring up a main content view with all details and shrink the tree into a sidebar view.
- The detailed view should include states, all subtasks or phases it ran, the node's compiled workflow, the state or result of every workflow level, AI summaries, timestamps for start and completion, and related runtime detail.
- The UI should expose operations like `git revert`, update or replace prompt, erase and rerun children, and similar runtime actions.
- The exact operation set still needs to be fleshed out against what the program actually supports.
- The website should be added to AGENTS as a sixth first-class system.
- Testing is paramount.
- Playwright should be able to test everything.
- Visual aspects that Playwright cannot judge should be screenshot and passed to an AI during review.
- Side-task idea: when the AI prompts the user for input, it should be able to provide a form rendered as HTML instead of only asking for a block of text.
- Example future form fields: textbox, checkbox, radio button, and similar structured input types.

## Immediate Open Questions

- What exact CLI operations already exist and are stable enough to map directly into web actions?
- Which UI reads should be flattened summaries versus on-demand detail fetches?
- Which actions are safe enough for single-click execution, and which require explicit review or confirmation flows?
- How should browser auth align with the daemon's current local token model?
- Which parts of the UI should be operator-first versus AI-session-first?

## Later Clarifications

Later notes in this folder narrowed or clarified several parts of this original braindump.

The most important later clarifications are:

- v1 does not require full CLI parity
- the website is operator-only
- project selection is about git repos or clone bases
- polling is acceptable for v1
- prompt update is in v1 and is paired with regeneration
- saved prompt drafts are deferred to v2
- most website data should reuse current daemon responses where practical
