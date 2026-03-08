# Code Vs YAML Delineation

## Purpose

This note defines the boundary between:

- the code runtime/daemon implementation
- the declarative YAML workflow layer

The current notes already describe:

- the daemon as the live orchestration authority
- the database as the durable canonical record
- YAML as source input that compiles into immutable workflows

What remains too fuzzy is which behaviors are:

- fixed runtime responsibilities
- configurable workflow responsibilities
- configurable policy inputs that still require fixed runtime enforcement

This note is meant to make that boundary explicit enough to guide implementation and to keep the `flows/` specs from smearing orchestration logic into YAML.

Related documents:

- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `flows/README.md`

---

## Core decision

### Short version

YAML defines:

- what exists
- what is allowed
- what should run
- what order or dependency relationships are intended
- what policies and gates apply

code defines:

- whether the requested operation is valid right now
- how state transitions happen safely
- how workflows are compiled
- how scheduling, locking, recovery, persistence, and reconciliation actually execute

### Practical rule

YAML should be declarative.

Code should be authoritative, stateful, and algorithmic.

If a behavior requires:

- coordination across live sessions
- durable state mutation
- concurrency control
- recovery safety
- git safety
- authoritative-version selection
- ambiguity resolution

then it belongs in code, even if YAML configures its policy.

---

## Primary boundary rule

Use this question:

> Is this describing desired structure/policy, or is it making a live coordination decision?

If it is structure or policy:

- YAML

If it is a live decision or durable mutation:

- code

---

## What YAML should own

YAML should own the declarative model of the system.

### 1. Node, task, and subtask definitions

YAML should define:

- node kinds
- tiers
- available tasks
- subtask sequences
- subtask types
- prompts
- command templates
- required artifacts
- validation/review/testing/docs hooks to invoke

Reason:

- these are workflow definitions, not orchestration decisions

### 2. Parent/child structural intent

YAML should define:

- allowed parent/child relationships
- layout definitions
- declared child IDs
- declared dependency edges
- required vs optional child semantics
- semantic ordering hints where applicable

Reason:

- this is declarative structure

### 3. Project policy

YAML should define policy inputs such as:

- max retries
- pause thresholds
- review/testing requirements
- auto-run child policy
- auto-merge policy
- concurrency limits as policy values
- allowed gate overrides
- environment requirements

Reason:

- policy should be configurable, but its enforcement still belongs to runtime code

### 4. Compile-time extensions

YAML should define:

- hooks
- overrides
- additional built-in or project task families
- review/testing/docs definitions
- rectification templates
- provenance extraction policy inputs

Reason:

- these shape the compiled workflow, but do not execute themselves

### 5. Human-facing instructions

YAML should define:

- prompts
- summary templates
- operator-facing guidance text
- AI-facing command-loop instructions

Reason:

- these are content, not runtime decisions

---

## What code should own

Code should own all authoritative execution behavior.

### 1. Compilation and validation engine

Code should own:

- loading YAML families
- merge and override resolution
- schema validation
- hook expansion
- canonical normalization
- compiled workflow generation
- compile-failure classification and persistence

Reason:

- compilation is an algorithmic authority boundary
- allowing YAML to define its own compiler behavior recursively will make the system unbounded and non-reproducible

### 2. Lifecycle and state transitions

Code should own:

- node lifecycle transitions
- run lifecycle transitions
- session lifecycle transitions
- pause/resume/cancel transitions
- supersession/cutover transitions

Reason:

- these are authoritative durable mutations

### 3. Scheduling and coordination

Code should own:

- run admission
- dependency readiness checks
- ready/blocked classification
- child scheduling
- concurrency control
- waiting behavior
- impossible-wait detection
- active locking

Reason:

- these are live orchestration decisions

### 4. Session and recovery logic

Code should own:

- tmux/session creation
- session binding and rebinding
- heartbeat tracking
- idle detection
- recovery classification
- replacement-session creation
- duplicate-session resolution

Reason:

- these depend on live runtime facts and recovery safety rules

### 5. Git orchestration and reconciliation

Code should own:

- branch creation and naming
- seed/final commit tracking
- ordered child merge execution
- conflict detection
- reset-to-seed behavior
- rectification
- cutover selection
- old-version active-run handling

Reason:

- git reconciliation is side-effecting and safety-critical

### 6. Persistence and audit emission

Code should own:

- writing durable rows and events
- ensuring post-decision persistence
- emitting summaries/events when runtime decisions occur
- maintaining read models for introspection

Reason:

- persistence cannot depend on workflow authors remembering to declare it correctly

### 7. Security and command authorization

Code should own:

- daemon API auth
- mutation authorization
- guardrails on destructive commands
- validation of legal transitions

Reason:

- security and mutation safety cannot be delegated to YAML

---

## Shared boundary: YAML configures, code enforces

This is the main middle ground.

Many important behaviors should be YAML-configurable but code-enforced.

Examples:

- retry limits
- gate ordering within allowed boundaries
- required review/testing stages
- child auto-run policy
- merge approval requirements
- environment selection policy
- allowed parent/child constraints

Rule:

YAML may describe the policy.

Code must:

- validate that the policy is legal
- compile it into a safe internal form
- enforce it durably at runtime

---

## What must never live only in YAML

The following should never be left to YAML-only semantics.

### 1. Live state mutation rules

Bad example:

- YAML declares exactly how to transition paused to resumed by mutating runtime state

Correct:

- YAML may declare that a pause gate exists
- code performs the legal transition and persists it

### 2. Scheduling algorithms

Bad example:

- YAML decides child scheduling or lock acquisition rules procedurally

Correct:

- YAML declares dependencies and policy
- code decides readiness and scheduling

### 3. Recovery decisions

Bad example:

- YAML specifies how to pick the winning session when multiple primary sessions exist

Correct:

- YAML may define whether recovery is allowed or bounded
- code performs the recovery classification and decision

### 4. Compile behavior itself

Bad example:

- YAML overrides define arbitrary compile-order logic or recursive compile semantics

Correct:

- YAML provides inputs to a fixed compiler pipeline implemented in code

### 5. Git safety decisions

Bad example:

- YAML directly defines merge conflict resolution or cutover behavior as free-form execution logic

Correct:

- YAML may define whether merge approval is required or which reconcile strategy family is requested
- code performs the git operations and conflict-safe state transitions

---

## Recommended delineation by flow

This maps the current `flows/` set into code versus YAML responsibilities.

### Flow 01: Create top-level node

YAML owns:

- node definition schema
- default tasks and policies

Code owns:

- request validation
- node version creation
- source resolution
- branch initialization
- compile trigger
- persistence

### Flow 02: Compile or recompile workflow

YAML owns:

- definitions, overrides, hooks, policies

Code owns:

- load order
- merge rules
- schema validation
- hook expansion algorithm
- compile-failure persistence

### Flow 03: Materialize and schedule children

YAML owns:

- layout definitions
- declared child graph
- parent/child constraints

Code owns:

- graph validation
- idempotent materialization
- child creation
- dependency persistence
- readiness classification
- scheduling

### Flow 04: Manual tree edit and reconcile

YAML owns:

- resulting authoritative layout or structural definitions

Code owns:

- authority-state tracking
- hybrid detection
- reconciliation gating
- mutation safety

### Flow 05: Admit and execute node run

YAML owns:

- task graph
- subtask types
- prompts and command templates
- gate requirements

Code owns:

- run admission
- cursor initialization
- session binding
- subtask dispatch
- attempt/state persistence
- legal advancement

### Flow 06: Inspect state and blockers

YAML owns:

- nothing runtime-authoritative here except definitions used to explain current workflow shape

Code owns:

- authoritative read assembly
- blocker classification
- lineage resolution

### Flow 07: Pause, resume, and recover

YAML owns:

- pause policies
- resumability policy inputs

Code owns:

- actual pause/resume/recovery decisions
- session replacement
- safety checks

### Flow 08: Handle failure and escalate

YAML owns:

- retry policy
- threshold policy
- escalation hooks

Code owns:

- failure classification
- threshold enforcement
- impossible-wait detection
- parent escalation decisions

### Flow 09: Run quality gates

YAML owns:

- gate definitions
- checks to run
- ordering policy within allowed bounds

Code owns:

- gate execution engine
- result persistence
- gate verdict calculation

### Flow 10: Regenerate and rectify

YAML owns:

- rectification policy inputs
- reusable workflow definitions for rebuilt nodes

Code owns:

- supersession creation
- rebuild orchestration
- old-run handling
- cutover decisions

### Flow 11: Finalize and merge

YAML owns:

- finalize policy
- merge approval requirement

Code owns:

- actual merge execution
- conflict handling
- final commit persistence
- lifecycle finalization

### Flow 12: Query provenance and docs

YAML owns:

- provenance/docs configuration families

Code owns:

- entity extraction
- identity matching
- confidence scoring
- docs build execution
- query assembly

### Flow 13: Human gate and intervention

YAML owns:

- which gates exist
- which operations require approval

C++ owns:

- gate creation
- legal decision validation
- resumed execution after decision

---

## Heuristic for deciding future ownership

When adding a new feature, classify it with these tests.

### Test 1: Is it content or control?

- content -> YAML
- control -> usually code

### Test 2: Is it static structure or dynamic coordination?

- static structure -> YAML
- dynamic coordination -> code

### Test 3: Does it require a legal state transition?

- yes -> code

### Test 4: Could a bad definition break recovery, auditability, or safety?

- yes -> code must enforce and likely own the algorithm

### Test 5: Is it something a project should customize without recompiling the runtime?

- yes -> probably YAML-configurable
- but still not necessarily YAML-executed

---

## Recommended hard rules

To keep the architecture coherent, freeze these rules.

### Rule A

YAML may declare workflow structure and policy, but it may not define new orchestration semantics at runtime.

### Rule B

Every YAML-defined subtask type must map to a code handler or a bounded handler family implemented in code.

### Rule C

YAML may select a strategy family, but code owns the algorithm.

Examples:

- YAML may choose `reconcile_strategy: ordered_child_merge`
- code implements ordered child merge

### Rule D

All durable state transitions are emitted by code, never by trusting YAML alone.

### Rule E

Compilation is one-way:

- YAML -> compiled workflow

Execution runs only the compiled workflow plus runtime state.

### Rule F

If a feature crosses process, session, or git boundaries, it is runtime territory by default.

---

## Specific planning gaps exposed by the current flows

The current `flows/` set makes these gaps visible.

### 1. Subtask type boundary is still too loose

The flows refer to things like:

- execute validation
- execute review
- execute finalize
- execute spawn child node

But the design still needs a tighter statement that:

- YAML picks the subtask type and parameters
- code dispatches to a closed handler set

### 2. Policy versus algorithm is not frozen sharply enough

Several flow files mention behavior such as:

- scheduling
- recovery
- reconciliation
- gate verdicts

The system needs a stronger statement that YAML can tune policy but cannot replace these algorithms.

### 3. Reconciliation strategy families need a bounded catalog

Right now the notes can be read as if rectification/reconciliation behavior is open-ended.

Safer model:

- YAML selects from a bounded strategy enum or strategy family
- code implements the allowed strategies

### 4. Read-model assembly belongs firmly to C++

The inspection flow makes it tempting to think YAML can shape read assembly.

It should not.

YAML may contribute labels or metadata, but authoritative current-state views must be runtime-owned.

### 5. Provenance extraction policy needs a sharper split

It is reasonable for YAML to configure what provenance families are desired.

It is not reasonable for YAML to define identity matching logic itself.

That matching logic belongs in code.

---

## Recommended next spec updates

To make this boundary implementation-ready:

1. update `flows/README.md` with a short boundary statement pointing back to this note
2. update the YAML spec to state that subtask types dispatch only to runtime-implemented handler families
3. update runtime docs with a closed inventory of handler families owned by code
4. add a bounded strategy catalog for reconcile, recovery, and gate behaviors where YAML can choose among safe runtime algorithms
5. update flow docs to distinguish:
   - declarative inputs
   - runtime-owned decisions
   - durable outputs

---

## Bottom line

The clean architectural split is:

- YAML defines the workflow language
- code implements the workflow engine

More concretely:

- YAML describes structure, policy, prompts, and permitted behavior
- code performs compilation, coordination, execution, recovery, persistence, reconciliation, and safety checks

If you keep that rule hard, the planning surface becomes much clearer and the `flows/` docs can evolve into implementation-facing orchestration specs without turning YAML into an unbounded second runtime.
