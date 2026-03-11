# Frontend Website Prompts And Regeneration Decisions

## Context

This note records the implementation decisions for the website prompt-history and supersede-plus-regenerate phase.

## Decisions

### Use the existing two-step daemon flow

The website should not invent a browser-only combined mutation endpoint for v1.

The prompt mutation flow should call:

1. `POST /api/nodes/{node_id}/supersede`
2. `POST /api/nodes/{node_id}/regenerate`

This keeps the browser aligned with existing daemon and CLI behavior.

### Regeneration may reuse the latest candidate version

Implementation review of `src/aicoding/daemon/regeneration.py` confirmed that regeneration checks the logical node selector and reuses the latest created candidate version if one already exists.

That means the browser can safely:

1. create a superseding candidate with the edited prompt
2. immediately call regenerate for the same logical node

without needing a special website-only mutation path.

### The prompt editor should target the latest created version

The editable prompt in the browser should not be derived only from the authoritative node summary.

Instead, the prompt tab should:

1. load node lineage
2. determine the latest created node version id
3. load that node version record
4. use that version's title and prompt as the editable baseline

This lets the browser present the latest candidate prompt when one already exists.

### Live candidate blocks new supersede

The browser should surface the existing daemon conflict honestly.

If `latest_created_node_version_id != authoritative_node_version_id`, the prompt tab should treat the node as already having a live candidate version and block another prompt supersede from the browser.

The tab should still render:

- latest version metadata
- current prompt text
- prompt history

but the edit mutation should be disabled with an explicit explanation.

### Confirmation stays inline

The prompt flow should not use modal dialogs.

The confirmation strip should appear inline in the prompt panel and offer:

- `save and regenerate`
- `discard changes`
- `keep editing`

### Refresh scope stays bounded

After a successful save-and-regenerate flow, the website should invalidate:

- the selected node's overview, lineage, workflow, runs, prompts, and actions queries
- project-scoped bootstrap/tree queries for the current project

The browser should stay on the same node and `prompts` tab.
