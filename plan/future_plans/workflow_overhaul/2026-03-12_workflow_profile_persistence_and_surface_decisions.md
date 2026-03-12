# Workflow Profile Persistence And Surface Decisions

## Purpose

Record the current future-plan decisions for:

- where workflow-profile state should live durably
- when explicit layout selection should be allowed
- how much profile-derived data should be frozen into compiled state
- what belongs in durable DB columns versus JSON payloads
- which built-in kinds should ship parentless
- which operator surface should be rich
- what the minimal `workflow brief` contract should be
- how prompt-bundle promotion should be staged

This is still a future-plan note.

It is not an implementation claim.

## Decision Summary

### 1. Selected workflow profile should live in two places, not one

Future intended rule:

- the selected workflow profile should be stored durably on the node version as the authoritative chosen configuration for that version
- the selected workflow profile and its resolved effective state should also be frozen into compiled workflow context for the specific compile attempt

Reason:

- node version needs to answer "what profile was this version configured to use?" even before or outside a successful compile
- compiled workflow needs to answer "what exact profile state was compiled into this workflow?" including resolved obligations, effective layout, and brief content

Implication:

- do not rely on `hierarchy_nodes` for selected workflow profile state
- prefer version-scoped configuration plus compile-scoped frozen snapshot

### 2. Reflect profile state in compiled tasks and compile context, not only as a top-level selector

Future intended rule:

- selected profile state must be reflected in the compiled workflow, not only stored as a request field or node-version attribute
- children and descendants should be able to inspect enough compiled context to understand where they sit in the tree and why their role/profile was chosen

Minimum compile-frozen profile payload should include:

- selected workflow profile id
- selected workflow profile name and description snapshot
- applies-to kind
- effective layout id
- child role to child profile defaults
- required child roles
- required repository updates
- required verification categories
- completion restrictions
- rigid step-order and blocked-action metadata for the current compiled workflow
- brief-generation settings
- upstream ancestry summary with ancestor node ids, titles, kinds, and selected profiles

### 3. `layout_id` should not be a first-class create/start input in the initial profile-aware slice

Future intended rule:

- initial profile-aware `workflow start` and `node create` should accept `workflow_profile`
- explicit `layout_id` should be deferred to the materialization layer first

Reason:

- startup/create selects the node's intended operating mode
- layout is primarily a decomposition/materialization concern
- the current runtime already has a distinct materialization phase and generated-layout registration path
- letting startup choose both profile and layout immediately would freeze precedence rules too early and make the first contract much harder to stabilize

Practical interpretation:

- first implementation: `workflow start --workflow-profile ...`
- later or same-adjacent follow-up if needed: `node materialize-children --layout ...`
- only add create/start-time `layout_id` if a later authoritative contract proves it is necessary

### 4. Freeze more profile-derived data into compiled state rather than less

Future intended rule:

- err on the side of more compile-frozen context, as long as the frozen payload is structured and inspectable

Reason:

- child and descendant execution needs stable context
- inspection surfaces should not have to recompute important planning context from drifting YAML every time
- compile failures and rebuilt versions must remain explainable later

So the compiled payload should likely include:

- selected profile descriptor snapshot
- effective layout descriptor snapshot
- recommended child roles and profiles
- ancestor-chain summary and current node position in that chain
- required updates and verification obligations inherited at this tier
- current blocked-step reasons and next-legal-step guidance
- prompt-reference metadata used to build the brief
- generated `workflow brief` payload itself or a durable equivalent

### 5. Use DB columns for stable selectors and filters; use JSON for richer evolving compiled detail

This is the intended DB split.

Use durable DB columns for data that is:

- used to identify, filter, join, or index records
- part of version identity or operator selection
- likely to appear in concise listings and route selectors

That likely means:

- `node_versions.selected_workflow_profile_id`
- possibly `compiled_workflows.effective_layout_id` if materialized/compiled inspection needs cheap filtering by layout

Keep richer evolving detail in JSON where shape is likely to expand and where the data is compile-specific rather than selector-specific.

That likely means:

- compiled workflow profile snapshot
- compatible layouts snapshot
- child role mappings
- required updates and verification categories
- completion restrictions
- ancestry/profile chain summary
- generated brief content
- recommended child descriptors

Why this split makes sense in the current schema:

- `node_versions` already holds version-scoped durable configuration like title, prompt, branch metadata, and authoritative compiled workflow link
- `compiled_workflows.resolved_yaml` already holds compile-frozen payloads and the database spec already acknowledges frozen `compile_context`
- adding every future workflow-profile detail as a first-class column would make migrations noisy and brittle for data that is better treated as a versioned compiled snapshot

What should not happen:

- do not hide the selected profile only inside `compiled_workflows.resolved_yaml.compile_context`, because then an uncompiled or failed-to-compile version loses its intended configured profile
- do not push large descriptive or recommendation-heavy brief payloads into top-level listing columns

### 6. All built-in `epic`, `phase`, `plan`, and `task` kinds should ship parentless-capable

This future decision is explicit.

Reason:

- they should all be runnable in isolation for testing, review, and focused execution
- top-level startup should remain structural and should not require an epic wrapper
- merge behavior remains a separate operator decision and does not require semantic top-level restrictions

### 7. `node kinds` should stay thin; `node types` should be the rich node-context surface

Future intended rule:

- keep `node kinds` as the thin global catalog
- do not add `node kinds --verbose` as the primary richer surface
- use `node types --node <id>` as the richer context-sensitive surface

Reason:

- `node kinds` answers "what kinds exist?"
- `node types` answers "what is legal and relevant for this current node context?"
- the richer response depends on selected profile, effective layout, allowed child kinds, recommended child roles, and runtime state that does not belong in one global catalog response

### 8. Minimal authoritative `workflow brief` should still be substantial

The minimal useful `workflow brief` should include:

- current node id and node version id
- current node title and kind
- selected workflow profile descriptor
- effective layout descriptor
- concise objective summary
- ancestor/profile chain summary so a child can understand where it sits in the tree
- required child roles and recommended child profiles
- required repository updates
- required verification categories
- completion restrictions that matter at this tier
- prompt-reference metadata or prompt-stack summary, not necessarily full prompt text
- CLI discovery note pointing to `node types` or `node profiles` for fuller catalog views

What the minimal brief should not try to be:

- a full dump of all compatible profiles and layouts
- a replacement for full compiled workflow inspection
- a raw prompt archive

### 9. Prompt-bundle promotion should be done in one authoritative planning task/note at a time, but the intended prompt bundle should be promoted as a coherent set

Future intended rule:

- do not promote prompt files piecemeal in a way that leaves one tier half-adopted
- but also do not mix prompt promotion into every unrelated runtime slice opportunistically

Recommended planning posture:

- open one dedicated authoritative planning task or feature slice for prompt-bundle adoption
- move the relevant prompt set coherently once the runtime contracts are ready

This keeps prompt adoption explicit and auditable without scattering it across many partially-related implementation slices.

### 10. Migration posture should be additive and version-oriented

Future intended rule:

- the first workflow-profile migration slice should be additive rather than restructuring existing runtime tables heavily
- prefer adding a small number of version-scoped selector columns and then using existing compiled JSON payloads for richer frozen state

Reason:

- the current schema already has the right durability split between version configuration and compiled execution state
- additive migrations are easier to roll out, backfill, and inspect honestly
- the workflow-overhaul bundle still expects some response and compile payload shapes to evolve

Recommended first migration direction:

- add `selected_workflow_profile_id` to `node_versions`
- do not introduce a large standalone profile-state table in the first slice
- do not split compile-context into many new relational tables before the runtime contracts are proven

### 11. `effective_layout_id` should not be a first-class DB column in the first implementation slice

Future intended rule:

- do not add `compiled_workflows.effective_layout_id` as a real column in the first profile-aware implementation slice
- store effective layout id and descriptor inside compile-frozen payload first

Reason:

- current runtime does not yet have a demonstrated indexed lookup or listing need that requires cheap relational filtering by layout
- effective layout is compile-specific and can be derived from compiled payload during early adoption
- adding the column too early would commit the schema before proving that the field actually needs column-level query performance

When a real column would become justified later:

- if operator listings or daemon routes need to filter or aggregate compiled workflows by effective layout often enough that JSON inspection becomes a measurable bottleneck

### 12. Route and response posture should stay additive and non-overlapping

Future intended rule:

- keep the existing thin `node kinds` and startup/create routes
- add new read surfaces rather than overloading the old thin ones
- keep route responsibilities distinct

That means:

- `GET /api/node-kinds` stays thin and global
- `GET /api/nodes/{node_id}/types` is the rich node-context type/layout surface
- `GET /api/nodes/{node_id}/profiles` is the profile-focused node-context surface
- `GET /api/nodes/{node_id}/workflow-brief` is the compact decision/context surface
- `GET /api/workflow-profiles` and `GET /api/workflow-profiles/{profile_id}` are repo-wide catalogs

Reason:

- the surfaces answer different questions
- keeping them additive avoids turning one route into a shape-shifting contract with unstable optional payload branches

### 13. Compile-context schema should be structured and sectioned, not one flat blob

Future intended rule:

- profile-aware compile context should be stored as a structured object with stable top-level sections
- do not flatten all workflow-profile data into one unbounded bag of keys

Recommended top-level sections:

- `profile`
- `layout`
- `ancestry`
- `obligations`
- `brief`
- `prompt_stack`
- `compile_variant`

Suggested intent of each section:

- `profile`: selected profile id plus frozen descriptor and applicability metadata
- `layout`: effective layout id, source, precedence result, and compatible-layout snapshot where needed
- `ancestry`: current node position and ancestor/profile chain summary
- `obligations`: required roles, repository updates, verification categories, and completion restrictions
- `brief`: generated objective and recommended-child payload
- `prompt_stack`: node-tier/profile/brief prompt refs and related metadata
- `compile_variant`: existing authoritative/candidate/rebuild context already used elsewhere in the runtime

### 14. Generated registered layouts should outrank profile defaults once registered

Future intended rule:

- generated registered layouts should remain the authoritative highest-priority layout source for a node version once they are explicitly registered
- explicit operator materialization override, if later adopted, should outrank profile default for that invocation but should not silently displace a registered generated layout permanently unless the contract says it supersedes it

Recommended precedence order:

1. explicit one-shot materialization override, if the command surface later supports it
2. registered generated layout for the current node version
3. selected profile default layout
4. built-in kind fallback layout

Reason:

- the current runtime already requires explicit registration for generated layouts rather than ambient discovery
- once a parent session or operator registers a generated layout, that act should mean "use this layout for this version"
- profile defaults should provide a baseline, not override a specifically generated decomposition artifact

## DB Elaboration

The current database model matters because the workflow-overhaul work will cut across three different durability layers:

### Layer 1: Structural configuration

Current examples:

- `hierarchy_nodes`
- `node_versions`
- `logical_node_current_versions`

This layer answers:

- what node/version exists?
- what was it configured to do?
- what is the authoritative version?

Future workflow-profile implication:

- selected workflow profile belongs here at the version level because it is part of version configuration

### Layer 2: Compiled frozen execution state

Current examples:

- `compiled_workflows`
- `compiled_tasks`
- `compiled_subtasks`

This layer answers:

- what exact workflow was compiled?
- what prompt/command/task chain was frozen?
- what compile-time context did this run use?

Future workflow-profile implication:

- effective profile snapshot, effective layout snapshot, brief payload, required obligations, and ancestry context belong here because they describe the compiled execution context

### Layer 3: Runtime execution and inspection

Current examples:

- `node_runs`
- `node_run_state`
- `node_lifecycle_states`
- workflow events and related inspection records

This layer answers:

- what happened when the node ran?
- what state is it currently in?
- how can an operator inspect what happened?

Future workflow-profile implication:

- runtime routes should read selected profile from version and frozen profile state from compiled workflow
- they should not have to reconstruct the node's meaning from live YAML only

## Resulting Future DB Direction

The future intended persistence direction is:

1. store the selected profile id on `node_versions`
2. freeze the full effective profile and brief context into compiled workflow payload
3. keep large evolving descriptive data in compiled JSON
4. only introduce extra first-class columns when the data needs filtering, indexing, or cheap operator listing

## Follow-On Implications For Authoritative Planning

When authoritative plans open later, they should treat the following as already-decided future direction unless a new contradiction is discovered:

- all built-in kinds ship parentless-capable
- top-level profile starts are legal through each profile's own `applies_to_kind`
- selected profile is version-scoped and compile-frozen, not only one or the other
- explicit layout override begins at materialization rather than startup
- `node types` is the richer node-context surface
- `workflow brief` is a compact decision-and-context payload, not a full catalog dump
- prompt-bundle adoption should be handled as one coherent planning slice rather than scattered across runtime slices
