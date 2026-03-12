# Node-Tree Copy/Paste Overview

## Purpose

Preserve a future idea for treating an existing node subtree as a reusable execution template.

The intended user value is:

- take a tree that already decomposed work well
- copy that tree from the top-level node through all descendants
- optionally export that copied tree as a shareable artifact
- paste it into a selected project with a clean starting snapshot
- replay the same hierarchy and prompts without asking the system to rediscover the child structure again

This is not an implementation plan.

It is a working note for a later feature direction.

## Position In The Roadmap

This idea should be treated as downstream of two other planning tracks:

- `plan/future_plans/workflow_overhaul/draft/`
- `plan/future_plans/frontend_website_ui/`

Reason:

- the workflow-overhaul direction is where richer profile-aware parent behavior, child-role semantics, and stronger decomposition contracts are being defined
- the frontend/web-UI direction is the most likely future place where operators would want to browse trees, choose a source tree, inspect what is being copied, select a destination project, and trigger paste/replay

This means the copy/paste idea is not "build this next."

It is "capture this now so it can be designed after those prerequisite surfaces are more stable."

## Core Idea

The future feature would have four closely related operator actions:

1. Copy tree
2. Export copied tree
3. Import exported tree
4. Paste tree

The copied or exported artifact is not just one node.

It is a full subtree package that includes:

- the selected root node
- every descendant down to bottom-level subtasks
- node kind and tier information
- parent-child edges
- dependency edges where applicable
- original prompts or prompt references needed for replay
- ordering and role information needed to preserve the original execution shape

If the tree is exported for sharing, the package would also likely need:

- a versioned artifact envelope
- provenance for the source tree it came from
- enough validation metadata to reject incompatible or tampered imports
- explicit separation between shareable structural data and non-shareable local runtime residue

The pasted or imported artifact would not be treated as a completed run clone.

It would be treated as a fresh runnable tree initialized from a copied structure.

## Export And Sharing Model

The new requirement is that copied trees should not be trapped inside one local runtime.

The future feature should support a shareable exported-tree artifact so that operators can:

- pass a proven tree template to another person
- move a tree template between environments
- preserve a useful decomposition pattern outside the source database

That implies three distinct concepts:

- copy: create a local reusable subtree package inside the current environment
- export: turn that package into a portable artifact
- import: validate a portable artifact and register it locally so it can be pasted

The safest starting assumption is that export should carry:

- structure
- prompts needed for replay
- dependency and ordering metadata
- provenance for where the artifact came from

and should not carry:

- live sessions
- in-progress run state
- opaque local machine paths that make the artifact non-portable
- completion claims from the original run as if they apply to the new pasted run

## Intended Paste Semantics

The best current reading of the idea is:

1. The operator selects either a locally copied tree artifact or an imported exported-tree artifact.
2. The operator selects the destination project during paste.
3. The system creates a fresh base-repo snapshot for that destination project.
4. That fresh snapshot becomes the starting base at the pasted epic level.
5. The full copied hierarchy is materialized durably under that new top-level parent.
6. The pasted tree begins in a stopped state.
7. When started, the top-level parent reuses its original prompt and runs as a fresh parent in the new project context.
8. That parent does not generate children from scratch.
9. Instead, it is told that predefined children already exist.
10. The parent starts or schedules those existing children according to their preserved structure and dependency rules.
11. Each copied child then repeats that same model for its own descendants until the leaf tasks run.

The key distinction is:

- structure is copied
- execution is new

This is not meant to copy historical completion state.

It is meant to copy an execution pattern.

If the tree came from an imported export, the destination runtime should still record:

- which export artifact was used
- where that export artifact originally came from
- which local paste operation created the new runnable tree

## What Gets Skipped

The specific stage being skipped is child generation for copied parents.

For a normal parent flow, a parent may:

- interpret its prompt
- generate or register a child layout
- materialize children from that layout
- then schedule those children

For a pasted parent, the intent is different:

- the children already exist
- the system should not ask the parent to invent a new child set
- the system should not silently regenerate a different structure from the prompt alone
- the parent should receive the equivalent of "your predefined children are already here"

That suggests a future runtime mode where copied parents move directly into:

- prompt-aware execution against an already-materialized subtree
- child readiness evaluation
- recursive scheduling/start logic

instead of:

- decomposition
- child-layout generation
- child-materialization discovery

## Predefined-Children-But-Not-Built-Yet State

One extra runtime distinction is needed for this idea.

A copied or imported tree can already know its descendants structurally before those descendants are actually ready to run in the destination project.

In particular:

- the pasted parent may already have predefined children
- those children may already be durably represented in the copied tree
- but some descendant git environments may still need to be created later
- and those environment-creation steps may themselves depend on upstream work finishing first

That means the runtime likely needs a state or substate equivalent to:

- predefined children exist
- descendant git environments not built yet
- blocked on dependency completion

This should not be flattened into:

- missing children

because the structure is already known.

It also should not be flattened into:

- ready to run

because the descendant runtime environments do not exist yet.

The practical value of this distinction is operator clarity.

The UI or CLI should be able to show:

- this parent already has its copied children
- child generation is not pending
- the reason descendants are not starting yet is that their git/runtime environments are still waiting on dependency completion

Without that state, the copied-tree replay model would be hard to diagnose.

## Relationship To Existing Tree-Authority Rules

This idea sits awkwardly between current manual and layout-generated tree models.

A pasted tree would likely need its own explicit authority explanation.

It is not purely:

- manual child insertion

and it is not purely:

- layout-generated child materialization from the current destination prompt

It is closer to:

- imported predefined subtree

That likely means a real implementation would need to answer:

- whether pasted children count as a new origin type
- whether copied parents carry a frozen child-authority record
- whether later regeneration is allowed to replace that copied structure
- how operators inspect the source of a pasted subtree versus a locally generated one

The important future invariant is that the runtime must never pretend a copied structure was freshly generated if it was actually imported from another tree.

## Fresh Snapshot Requirement

The destination project matters.

The pasted tree should not inherit the old source repository state from the original run.

Instead:

- the operator chooses the destination project during paste
- the system creates a fresh starting snapshot from that destination project's base repo state
- that snapshot is applied at the pasted epic level
- descendant work then proceeds from that fresh destination baseline

This matters because the point of the feature is reuse of orchestration structure, not reuse of stale branch state.

The future implementation would need to define:

- exactly which branch, commit, or repository baseline is snapshotted
- whether the destination can be any configured project or only specific repos
- how provenance records tie the pasted run back to the copied source tree and the selected destination base snapshot

## Prompt Reuse Model

The note assumes prompt reuse is central.

When replay begins:

- the pasted epic should use the original epic prompt
- pasted phases should use their original phase prompts
- pasted plans should use their original plan prompts
- pasted tasks should use their original task prompts

That does not necessarily mean every prompt must be immutable forever.

It means the initial replay contract should preserve the same prompt inputs that originally shaped the copied tree.

Future open questions include:

- whether operators can edit prompts before starting the pasted tree
- whether prompt edits invalidate the copied-child guarantee
- whether prompt edits require a partial regeneration path rather than strict replay

## Runtime Shape

The future runtime model probably needs a distinct paste/replay flow:

### Stage 1: Source-tree packaging

- choose a root node to copy
- capture the full descendant tree
- capture durable structural metadata
- capture prompt and dependency information required for replay

### Stage 2: Destination-tree creation

- choose destination project
- create fresh top-level base snapshot
- materialize a new stopped top-level node and all descendant nodes
- record copied-from provenance
- mark descendants as predefined even if some of their git environments are still deferred

### Stage 3: Replay startup

- start the top-level parent
- inject the original prompt and copied-tree context
- tell the parent that its predefined children already exist
- skip child-generation work

### Stage 4: Recursive descendant replay

- children run with their original prompts
- when a child becomes dependency-ready, build or activate the git environment needed for its subtree if that environment was still deferred
- children schedule or start their own predefined descendants
- dependency and blocker rules still apply

### Stage 5: Normal completion and merge behavior

- once replay is underway, nodes should behave like ordinary live nodes
- summaries, failures, retries, and audits should still be durable and inspectable

## Main Risks And Design Questions

### Copied structure versus live adaptation

If the destination repo is meaningfully different from the original source repo, the copied tree may no longer fit cleanly.

That means the future feature may need a clear distinction between:

- strict replay
- replay with operator edits
- replay followed by selective regeneration

### Provenance must stay explicit

Operators need to be able to inspect:

- which tree was copied
- when it was copied
- which destination project it was pasted into
- which base snapshot was used
- whether the pasted tree was started yet

Without that, copy/paste would become hard to audit.

### Parent runtime semantics need an explicit mode

Current parent flows center on child generation/materialization plus scheduling.

This idea requires a parent mode closer to:

- predefined-child replay

That mode should be explicit, not inferred loosely from missing layout files.

### Predefined structure and built runtime must not be conflated

The runtime needs to distinguish between:

- child structure already known
- child git environment already built
- child actually ready to start

If those are collapsed into one status, operators will not be able to tell whether a node is waiting on:

- child generation
- environment creation
- normal dependency completion

### Large-tree cost could be significant

A full epic-to-subtask copy or export could be large.

A later implementation would need to think about:

- subtree serialization size
- export artifact size
- import validation time
- paste latency
- destination-tree creation speed
- operator inspection usability for very large copied trees

## Working Recommendation

Treat this as a later orchestration primitive for reusing proven workflow structures.

When it is revisited, the first design pass should probably define:

1. the copied-tree and exported-tree artifact shapes
2. the export/import plus paste command or API contracts
3. the fresh-snapshot provenance model
4. the parent runtime mode for predefined children
5. the boundary between strict replay and editable replay

Without those five pieces, implementation would drift into ad hoc cloning and file-sharing behavior.
