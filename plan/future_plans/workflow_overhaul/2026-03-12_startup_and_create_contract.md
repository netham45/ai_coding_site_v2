# Workflow Overhaul Startup And Create Contract

## Purpose

Define the intended future contract for profile-aware startup and node creation in the workflow-overhaul direction.

This note is a future-plan contract draft.

It is not an implementation claim.

## Why This Contract Comes First

The current runtime already has a clear daemon-owned startup boundary:

- `workflow start` creates a parentless node
- captures source lineage
- compiles the workflow
- transitions the node to `READY`
- optionally admits the first run

That makes startup/create the best first workflow-overhaul contract to freeze, because later schema, compile, materialization, and inspection slices all depend on the meaning of:

- how a selected workflow profile enters the system
- where that selection is persisted
- which nodes may start top-level
- what the mutation responses promise

## Existing Runtime Baseline

Current real surfaces:

- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/cli/handlers.py`
- `src/aicoding/daemon/models.py`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

Current implemented behavior:

- `WorkflowStartRequest` accepts `kind`, `prompt`, optional `title`, and `start_run`
- `NodeCreateRequest` accepts `kind`, `title`, `prompt`, and optional `parent_node_id`
- `node create --compile [--start-run]` currently proxies into `/api/workflows/start` when parentless
- startup legality is currently determined by hierarchy `allow_parentless`
- startup response is intentionally compact and does not include a large planning/brief payload

## Contract Goals

The future startup/create contract should:

- let a node version be created with an explicit selected workflow profile
- preserve daemon ownership of top-level create-and-compile startup
- preserve hierarchy-driven legality for top-level startup
- keep parented manual creation distinct from top-level composite startup
- keep startup responses compact enough for operator use and automation

## Mutation Surfaces

### Surface 1: `workflow start`

Purpose:

- create a new parentless node version and compile it as a daemon-owned startup action

Future request shape:

- `kind`
- `prompt`
- optional `title`
- optional `workflow_profile`
- optional `start_run`

Not included in the initial profile-aware startup slice:

- first-class `layout_id`

Reason:

- startup selects node operating mode
- explicit layout override belongs first at materialization time

### Surface 2: `node create`

Purpose:

- create a node directly, either as a manual child or as a parentless node when the operator wants the `node` namespace

Future request shape:

- `kind`
- `title`
- `prompt`
- optional `parent_node_id`
- optional `workflow_profile`

Expected behavior split:

- with `parent_node_id`: manual child creation, no implicit compile/start composite behavior
- without `parent_node_id` and with `--compile` or equivalent top-level flags: use the startup path semantics rather than inventing a second top-level lifecycle implementation

## Persistence Rules

### Rule 1: selected profile is version-scoped configuration

The selected workflow profile must be stored on the created `node_version`.

Reason:

- it is part of the version's configured operating mode
- it must remain visible even if compile fails
- a later candidate or regenerated version may intentionally choose a different profile

### Rule 2: compile freezes the effective profile state separately

After compile, the effective profile and related derived context must also be frozen into compiled workflow payload.

Reason:

- compile may resolve more than the requested profile id alone
- runtime inspection needs the exact compiled context, not only the requested selector

## Legality Rules

### Rule 1: top-level legality stays structural

Top-level startup is legal when:

- the requested node kind exists
- its hierarchy definition allows parentless creation
- the selected workflow profile, if supplied, applies to that kind

Top-level startup is not limited by tier semantics such as "only epics may start."

### Rule 2: built-in kinds are all intended top-level starts

Future built-in direction:

- `epic`
- `phase`
- `plan`
- `task`

should all be valid parentless startup kinds.

### Rule 3: profiles start through their own kind

If a profile applies to `phase`, `plan`, or `task`, it should be startable top-level through that kind when the kind is parentless-capable.

Examples:

- `phase.discovery` starts as a `phase`
- `plan.execution` starts as a `plan`
- `task.docs` starts as a `task`

## Title Rules

The current title behavior should largely remain:

- explicit title wins
- when omitted on `workflow start`, daemon resolves a title from prompt text

The selected workflow profile should not force different title semantics in the first profile-aware slice.

## Compile And Run Rules

### Rule 1: startup remains a composite mutation

Profile-aware `workflow start` should still:

1. create node and version
2. persist selected workflow profile on the version
3. capture source lineage
4. compile
5. transition lifecycle to `READY` on success
6. optionally admit the first run

### Rule 2: compile failure keeps configured profile visible

If compile fails:

- the node version should still retain the selected workflow profile
- compile failure payload should include compile-context metadata that reflects the attempted profile-aware startup

### Rule 3: startup should compile rigid workflow legality, not permissive narratives

If the selected profile is decomposition-required, the compiled workflow produced at startup should already freeze:

- required child roles
- step-order legality
- completion restrictions
- subtask completion predicates needed for later mutations

The runtime should not wait until a later prompt turn to decide whether skipping decomposition is legal.

## Response Rules

The startup/create mutation responses should remain compact.

They should include:

- created node identity
- resolved title
- selected workflow profile id or compact descriptor
- compile outcome
- lifecycle result
- run/session result when startup requests run admission

They should not include by default:

- the full `workflow brief`
- the full supported profile catalog
- the full compatible layout catalog

Reason:

- mutation responses should confirm what happened
- richer planning/context inspection belongs on `workflow brief`, `node types`, and `node profiles`

## CLI Contract Direction

### `workflow start`

Future intended flag:

- `--workflow-profile <id>`

No initial first-class flag:

- `--layout <id>`

### `node create`

Future intended flag:

- `--workflow-profile <id>`

Top-level behavior:

- parentless `node create --compile` or equivalent still routes through the startup lifecycle

### `node materialize-children`

This is where explicit `--layout <id>` should first become a real candidate mutation selector if later adopted.

## Failure Classification Direction

Profile-aware startup should fail clearly when:

- the requested profile id does not exist
- the profile does not apply to the requested node kind
- the requested kind is not parentless-capable for top-level startup
- compile fails after creation because profile/layout/compiler validation rejects the configuration

Later runtime mutations on the created node should also fail clearly when:

- required decomposition steps are skipped
- merge is attempted before child materialization or required child completion
- node completion is attempted before the compiled workflow's completion predicates are satisfied

These should remain separate failure classes instead of collapsing into one generic startup error.

## Out Of Scope For This Contract

This contract does not yet freeze:

- detailed `workflow brief` payload shape
- detailed `node types` or `node profiles` payload shapes
- materialization-time layout override semantics beyond saying they happen later than startup
- full compile-context JSON schema

Those belong to adjacent contracts.

## Expected Proof For The Later Authoritative Slice

The later real implementation slice should prove:

- top-level startup with `workflow_profile` for each shipped parentless kind family
- clear rejection for mismatched kind/profile combinations
- persisted selected profile visibility on created versions, including compile-failure cases
- compact startup responses that expose selected profile without dumping the full brief/catalog payloads
- CLI parity for `workflow start` and parentless `node create --compile`

## Relationship To Adjacent Future Notes

This contract should be read together with:

- `2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `2026-03-12_authoritative_plan_family_breakdown.md`
- `2026-03-10_workflow_profile_route_design.md`
