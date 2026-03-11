# Node-Tree Copy/Paste Working Notes

This folder captures a future idea for copying or exporting a whole node subtree and later importing or pasting it back into a selected project as a replayable execution template.

This is a working-note bundle, not an implementation plan.

Nothing in this folder should be read as an implementation, verification, or completion claim for the current repository.

## Bundle Contents

- `2026-03-11_original_starting_idea.md`
- `2026-03-11_copy_paste_tree_overview.md`
- `2026-03-11_roadmap_placement_and_open_questions.md`

## Working Intent

The main question in this bundle is:

How do we copy or export an existing epic-to-subtask tree and replay that exact structure in a different selected project without rerunning child generation?

The rough intended shape is:

- copy a subtree from the chosen top-level node all the way to leaf subtasks
- optionally export that subtree as a shareable artifact
- paste it into a selected base project
- create a fresh base snapshot at the pasted epic level
- keep the pasted tree stopped initially
- tell parent nodes they already have predefined children
- reuse the original prompts when the tree starts running
- let execution recurse downward through the preserved hierarchy until the copied work pattern has replayed

This bundle is intentionally future-facing.

It assumes this idea would only make sense after the repository has stronger support for:

- workflow-profile-aware decomposition from `workflow_overhaul/`
- a richer operator surface, likely including the future browser UI direction
- clearer manual-vs-generated child authority and replay semantics
