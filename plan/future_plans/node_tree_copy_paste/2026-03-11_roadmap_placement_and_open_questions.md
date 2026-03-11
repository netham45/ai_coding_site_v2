# Roadmap Placement And Open Questions

## Roadmap Placement

The intended ordering for this idea is:

1. workflow-overhaul planning and implementation
2. frontend/web-UI planning and implementation
3. node-tree copy/paste planning
4. later copy/paste implementation work

Why this ordering makes sense:

- workflow-overhaul is where the repository is defining stronger parent contracts, child-role semantics, and reusable decomposition shapes
- the web UI is the likely future operator surface for browsing source trees and selecting paste destinations
- copy/paste depends on both of those layers being clearer before its own contracts can be frozen responsibly

## Five-System Reading

If this ever becomes real work, it likely touches all five required systems:

- Database: copied-tree provenance, exported-artifact identity, pasted-tree identity, destination snapshot lineage, and replay-mode durability
- CLI: copy, export, import, and paste commands plus inspection surfaces for copied artifacts, exported artifacts, and pasted runs
- Daemon: authoritative packaging, export/import validation, paste-time validation, stopped-tree creation, and predefined-child replay behavior
- YAML: possible policy fields for whether a kind/profile allows copy, export, replay, prompt edit before replay, or selective regeneration after paste
- Prompts: replay-aware parent prompts that acknowledge predefined children instead of generating them, even when the tree arrived through an imported artifact

## Likely Invariants

Any future implementation should defend at least these invariants:

- a pasted tree must have explicit provenance back to its copied source tree
- an imported export must preserve explicit provenance back to its source tree and export artifact identity
- a pasted tree must have explicit provenance for the destination project and fresh base snapshot used at paste time
- copied replay must not silently claim that children were newly generated if they were imported
- copied replay must not silently claim that a descendant is runnable merely because its predefined structure exists when its git environment is still unbuilt
- the pasted parent must start stopped unless the operator explicitly starts replay
- recursive child start must still respect dependency readiness and blocking rules
- the original prompts used for replay must remain inspectable even if later edits are allowed

## Open Questions

### What is the copied artifact boundary?

Possible answers:

- only structure and prompts
- structure, prompts, and selected metadata
- structure, prompts, metadata, and reusable artifacts or summaries

The safest first interpretation is probably:

- structure plus prompt-and-dependency context

not:

- full historical run output cloning

### What is the export format and trust model?

Possible directions:

- daemon-issued JSON bundle
- signed archive with manifest
- export package plus separately referenced prompt or artifact files

The core questions are:

- how imports validate schema compatibility
- whether exports need signatures or hashes
- whether sensitive local fields must be stripped before sharing
- how much historical provenance should travel with the exported tree

### Does paste always create a new epic?

The current idea points that way because the fresh destination snapshot is applied at the epic level.

That suggests paste is primarily:

- top-level subtree import

rather than:

- arbitrary mid-tree grafting

### Can the pasted tree be edited before starting?

The idea as written emphasizes faithful replay.

A later design pass should choose whether v1 is:

- paste and replay only

or:

- paste, inspect, optionally edit, then replay

### How does later regeneration interact with copied parents?

If a copied phase is later regenerated, does it:

- lose copied-child status
- preserve child identities where possible
- require operator confirmation before replacing imported structure

This needs to align with the existing hybrid/manual/layout authority contracts.

### What is the runtime state model for predefined but not-yet-built descendants?

The future implementation likely needs an explicit state or status facet for:

- predefined descendant exists
- git environment not built yet
- waiting on dependencies before environment creation and start

Otherwise operators and automation will not be able to distinguish:

- generation not done
- environment not built
- environment built but blocked from start

This likely affects database state vocabulary, daemon scheduling logic, CLI/UI inspection surfaces, and possibly prompt wording for replay-aware parents.

### Where should the operator trigger copy and paste?

The likely surfaces are:

- CLI first
- web UI later
- both, with one daemon-owned backend contract

The important point is that the backend contract should be shared.

### Are exported trees only for this repository, or future cross-repo use?

The narrower and safer first assumption is:

- exported trees are portable between compatible instances of this orchestrator

not:

- arbitrary import into unrelated systems with no shared schema or prompt/runtime contract

## Suggested First Follow-On Notes

If this future direction remains interesting, the next useful planning notes would be:

1. a copied-tree and exported-tree artifact schema draft
2. an export/import plus paste API and CLI contract draft
3. a replay-mode prompt and runtime contract note, including the predefined-but-not-built-yet state model
4. a provenance and audit record draft for copied, exported, imported, and pasted trees
