# Common User Journeys Analysis

## Purpose

This note summarizes the most likely common user journeys implied by the current design notes, what each journey needs at a programmatic level, and which critical use cases still look under-accounted-for.

It is a synthesis of the current notes, especially:

- `notes/explorations/original_concept.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/archive/superseded/cli_surface_spec_revised.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#primary-session-lifecycle`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## What “common” means here

The notes describe a very broad system, but the highest-frequency usage is likely to concentrate around a smaller set of workflows:

1. starting new work from a prompt
2. decomposing that work into children
3. running and supervising active work
4. inspecting status, blockers, outputs, and rationale
5. recovering from interruptions or failures
6. modifying or regenerating work after new information appears
7. approving, reconciling, and finalizing results

These are the journeys most likely to dominate both user interaction and implementation effort.

---

## Journey 1: Create a top-level node from a prompt

### User intent

The user wants to tell the system “build this thing” and have the runtime turn that into a concrete executable node tree.

Typical examples:

- create a plan for a small feature
- create a phase or epic for a larger initiative
- start from a vague prompt and let the system scaffold structure

### Likely frequency

Very high. This is the primary product entrypoint.

### Programmatic requirements

- CLI mutation surface for node creation
- CLI mutation surface for one-shot top-level workflow start
- prompt capture and storage
- node-kind and tier resolution
- source YAML selection
- override resolution
- immutable workflow compilation
- node version persistence
- initial branch/seed metadata creation
- initial node lifecycle state creation
- initial run creation or deferred run-admission decision
- audit trail for source docs, prompt lineage, and compiled workflow lineage

### Core subsystems involved

- node creation runtime
- YAML schema and built-in library
- override merge logic
- workflow compiler
- DB persistence for node versions and workflows
- git initialization metadata
- operator CLI

### Critical completion conditions

- the created node is durable and inspectable
- the user can see what workflow was compiled
- the node can be started or resumed later without hidden state

Implementation staging note:

- the current runtime now satisfies the one-shot entrypoint with `workflow start`, which creates a top-level node, compiles it, and optionally starts the first run in one daemon-owned flow
- the equivalent `node create --compile [--start-run]` path is also now available for top-level kinds

---

## Journey 2: Auto-decompose a parent into child work

### User intent

The user wants a parent node to produce child tasks/phases/plans and schedule them, instead of manually creating each one.

Typical examples:

- a plan creates one or more task children
- an epic creates phases
- a parent regenerates its layout after research or review

### Likely frequency

Very high for the core orchestration story.

### Programmatic requirements

- layout-generation subtasks
- layout validation
- parent/child constraint validation
- dependency graph validation
- child materialization into durable node versions
- idempotent materialization behavior
- initial child branch and workflow setup
- parent-child edge persistence
- sibling dependency edge persistence
- ready/blocked child scheduling logic
- parent wait behavior for child completion

### Core subsystems involved

- compiled subtask execution
- child materialization and scheduling runtime
- dependency validation
- lifecycle state model
- DB persistence for children and dependency edges
- parent orchestration logic

### Critical completion conditions

- rerunning the same layout does not create duplicate children
- invalid layouts fail before partial child trees become authoritative
- the parent can explain why a child is ready, blocked, failed, or superseded

---

## Journey 3: Manually build or edit the tree

### User intent

The user wants direct control over the structure instead of relying fully on automatic decomposition.

Typical examples:

- manually create a child node
- replace a generated layout with a hand-authored one
- add a one-off child under an otherwise layout-driven parent

### Likely frequency

High. The notes explicitly position manual control as a core requirement.

### Programmatic requirements

- CLI mutation surfaces for manual child creation and layout replacement
- parent/child constraint checks
- hybrid tree authority tracking
- child-origin metadata
- reconciliation rules when manual edits touch layout-managed structures
- rebuild-trigger logic when manual edits affect authoritative structure
- audit trail for who/what changed the tree shape

### Core subsystems involved

- operator CLI
- config/update runtime
- child authority model
- reconciliation/pause logic
- source lineage persistence

### Critical completion conditions

- manual edits are not silently overwritten by later layout regeneration
- layout updates are not silently ignored when the subtree has become hybrid
- the parent has an explicit structural authority state: manual, layout-driven, or hybrid

---

## Journey 4: Run a node through the AI command loop

### User intent

The user wants the node to actually perform work: retrieve prompts, execute subtasks, register outputs, and advance through validations toward completion.

Typical examples:

- a task writes code and marks subtasks complete
- a review/test/doc stage runs after implementation
- an AI session pauses because it needs user input or cannot proceed

### Likely frequency

Very high. This is the runtime core.

### Programmatic requirements

- node run admission
- primary session binding
- tmux-backed session creation/attachment
- current cursor retrieval
- compiled subtask prompt/context retrieval
- deterministic stage-start context assembly from durable state
- subtask attempt creation
- heartbeat handling
- summary registration
- artifact/output persistence
- validation, review, and testing stage execution
- workflow advancement logic
- pause/failure handling
- finalization logic

### Core subsystems involved

- daemon/runtime orchestrator
- AI-facing CLI
- run/lifecycle state tables
- session tables and heartbeat tracking
- validation/review/testing runtimes
- summary persistence

### Critical completion conditions

- no subtask progression depends on hidden in-memory state
- a restarted or replacement session can retrieve the same startup context for the current stage without relying on terminal history
- the current subtask and attempt are always queryable
- validation/review/testing outcomes gate advancement deterministically

Implementation staging note:

- the current runtime now satisfies this startup-context requirement with a daemon-assembled `stage_context_json` returned by both `subtask prompt` and `subtask context`
- that bundle is built from durable node/run/workflow state, dependency blockers, recent prompt/summary history, and cursor-carried child/reconcile overlays rather than session-local memory
- primary-session binding now also creates a concrete long-lived tmux-backed shell with durable identity and attach metadata instead of a placeholder short-lived harness command
- `session show-current` now exposes the bound logical node id, node kind/title, run status, and recovery classification, so the first bootstrap read can confirm whether the active shell is healthy or stale before any node-specific retrieval command runs

---

## Journey 5: Inspect current state, blockers, and outputs

### User intent

The user wants to understand what is happening right now without attaching to implementation details manually.

Typical examples:

- show tree and status
- inspect current task/subtask
- inspect dependency blockers
- inspect prompts, summaries, logs, and outputs
- inspect compiled workflow and source YAML

### Likely frequency

Very high. A system this complex will be unusable without strong introspection.

### Programmatic requirements

- read-only CLI for node, run, workflow, task, subtask, session, dependency, git, and YAML views
- current-cursor views
- blocker classification surfaces
- prompt/context/output retrieval
- summary history
- source-lineage and override-lineage inspection
- merge/conflict inspection

### Core subsystems involved

- operator CLI
- read models/views in the DB
- workflow lineage and summary persistence
- dependency status classification

### Critical completion conditions

- users can answer “what is it doing?”, “why is it blocked?”, and “what changed?” from the CLI alone
- read paths expose the authoritative run/node version, not ambiguous candidate state

---

## Journey 6: Pause, resume, recover, or nudge work

### User intent

The user wants interrupted or idle work to continue safely instead of being lost or duplicated.

Typical examples:

- resume after terminal detach
- recover after tmux/session loss
- replace a lost session while preserving cursor state
- nudge an idle agent

### Likely frequency

High. Long-running AI work will hit this constantly.

### Programmatic requirements

- pause and resume CLI commands
- active run lookup
- resumability checks
- session heartbeat tracking
- tmux session existence checks
- replacement-session creation
- recovery decision logic
- duplicate-session detection
- git-head safety checks before resume
- recovery and pause event persistence

### Core subsystems involved

- recovery runtime
- session model
- lifecycle state model
- tmux/session integration
- run cursor persistence
- git state validation

### Critical completion conditions

- the system reuses an existing healthy session when safe
- it creates a replacement session when needed without losing cursor state
- it refuses unsafe resume when git or session ownership is ambiguous

---

## Journey 7: Handle failure, review findings, or blocked dependencies

### User intent

The user wants the system to stop failing opaquely and instead provide a structured path forward.

Typical examples:

- a subtask fails repeatedly
- a child fails and the parent must decide whether to retry, replan, or escalate
- a dependency target becomes impossible to satisfy
- review or validation blocks finalization

### Likely frequency

High. This will be a dominant operational path in real projects.

### Programmatic requirements

- subtask failure persistence
- failure counters and thresholds
- parent failure decision logic
- dependency impossible-wait detection
- pause-for-user logic
- structured summary registration for failures
- review-result persistence
- test-result persistence
- validation-result persistence
- clear blocked-state introspection

### Core subsystems involved

- runtime failure handler
- parent orchestration logic
- dependency validator/scheduler
- review/testing/validation frameworks
- pause and summary models

### Critical completion conditions

- the runtime never waits forever on an impossible dependency
- parent-facing failure decisions are durable and inspectable
- users can distinguish implementation failure from planning failure from structural graph failure

---

## Journey 8: Regenerate or rectify work after changes

### User intent

The user wants to change a prompt, layout, override, or child result and have the system rebuild the affected subtree sanely.

Typical examples:

- regenerate a node with better instructions
- rectify upstream after a child changed the assumptions of its parent
- rebuild a subtree without discarding unrelated valid siblings

### Likely frequency

High. The design explicitly treats regeneration as a core feature.

### Programmatic requirements

- node supersession/versioning
- rebuild event tracking
- authoritative-version selection
- old-version active-run handling
- seed/final commit tracking
- deterministic merge/reconcile pipeline
- conflict persistence
- selective child reuse rules
- cutover policy
- operator approval gates for risky mutations

### Core subsystems involved

- rectification runtime
- git branch/merge model
- node version lineage
- conflict handling
- authoritative-version logic

### Critical completion conditions

- rebuilt nodes create new versions instead of mutating old ones in place
- old active runs are handled explicitly, not implicitly abandoned
- authoritative lineage is clear during mixed old/new states

---

## Journey 9: Approve, merge, finalize, and publish results

### User intent

The user wants completed work to be reconciled into the parent or base branch only after the required gates pass.

Typical examples:

- finalize a task after validation/review/testing
- merge child results into the parent
- approve a gated merge to parent or base

### Likely frequency

High in any real workflow, though less frequent than status inspection or subtask execution.

### Programmatic requirements

- finalization ordering
- merge-event persistence
- conflict detection and resolution handling
- approval-gate handling
- final commit persistence
- node completion transition logic
- summaries and rationale capture before finalize
- optional docs/provenance generation ordering

### Core subsystems involved

- finalization runtime
- git integration
- gate/pause logic
- quality-gate frameworks
- merge audit models

### Critical completion conditions

- finalization is blocked if required gates fail
- merge order and outcome are durable and reproducible
- users can inspect what was merged, from where, and why

---

## Journey 10: Query rationale, provenance, and documentation

### User intent

The user wants to understand why code exists, what changed it, and which node/prompt introduced it.

Typical examples:

- inspect prompt lineage for a file or entity
- inspect entity history across edits
- generate docs for a node or subtree
- answer “which task introduced this function?”

### Likely frequency

Medium to high. This is one of the product’s differentiators, even if it is less frequent than run control.

### Programmatic requirements

- code-entity extraction
- stable or confidence-scored entity identity matching
- node-to-entity change linking
- code relation extraction
- provenance query surfaces
- docs build and retrieval surfaces
- rationale and summary taxonomy

### Core subsystems involved

- provenance model
- entity matching/extraction pipeline
- docs generation runtime
- CLI read surfaces for prompts, summaries, rationale, and entity history

### Critical completion conditions

- provenance survives ordinary refactors reasonably well
- uncertain matches are marked as uncertain
- rationale can be queried without relying on informal logs or memory

---

## Most common journeys by expected usage

If the product is used regularly, the likely ranking is:

1. inspect status/blockers/outputs
2. run a node through the AI command loop
3. create a top-level node from a prompt
4. auto-decompose into children
5. pause/resume/recover/nudge work
6. handle failures and blocked dependencies
7. manually adjust tree structure or layouts
8. regenerate/rectify after changes
9. approve/merge/finalize
10. inspect provenance/docs/rationale

This ranking matters because the product should optimize first for operational clarity, not only for initial planning.

---

## Cross-cutting implementation capabilities every common journey depends on

These are the capabilities that show up repeatedly across nearly all journeys:

- durable node versioning
- immutable workflow compilation
- strong read-only introspection CLI
- AI-facing command loop CLI
- durable run cursor persistence
- explicit session binding and recovery
- dependency validation and readiness classification
- pause/failure/gate event persistence
- authoritative lineage selection during supersession
- audit trail for prompts, summaries, workflows, merges, and source YAML

If any of these are weak, multiple top journeys degrade at once.

---

## Critical use cases that still look under-accounted-for

These are not minor implementation details. They affect whether the common journeys above actually work in practice.

### 1. Blocker-first operational introspection

The docs have strong generic read surfaces, but “why is this blocked right now?” still looks weaker than it should be for daily use.

Needed:

- explicit blocker model
- `node blockers` style surface
- clear distinction between dependency block, pause gate, failed child, compile failure, review gate, and session-loss block

Why it matters:

- this will likely be the most common user question in production

### 2. Compile-failure as a first-class user journey

Compilation of YAML/workflows is already covered in a dedicated note, but the operator journey for “my node or override does not compile” still feels secondary relative to the main create/run/inspect flows.

Needed:

- explicit compile-failure inspection surface
- compile-failure summaries/evidence
- clear retry/fix/regenerate flow from compile failure

Why it matters:

- creation, override updates, and regeneration all depend on compilation succeeding

### 3. Manual-tree plus auto-tree reconciliation UX

The hybrid-tree rules exist, but the user-facing reconciliation flow still looks under-defined for a common real-world case.

Needed:

- explicit reconciliation command(s)
- preview of structural diffs
- clear choices: preserve manual, adopt layout, merge into new authority

Why it matters:

- once real users start editing trees manually, hybrid state becomes normal, not exceptional

### 4. Old-version active-run handling during supersession

This is listed as an open gap and it affects regeneration directly.

Needed:

- precise policy for what happens to an active run on a superseded node version
- visible authoritative/candidate status in all current-state views
- safe cancellation/resume/cutover behavior

Why it matters:

- without this, regeneration can produce ambiguous live execution ownership

### 5. Impossible-wait and deadlock diagnosis

Invalid graph handling exists conceptually, but the day-to-day operator flow for impossible waits still needs stronger surfaces.

Needed:

- runtime impossible-wait detection
- direct explanation of the broken edge or stale target
- parent-facing and user-facing escalation path

Why it matters:

- waiting forever is one of the easiest ways for orchestration systems to feel broken

### 6. Review/testing execution as an operator workflow

Read models exist more clearly than mutation/execution flows for review/testing.

Needed:

- explicit commands to run review/testing where policy allows
- persisted findings/results schema
- clear gating effect on finalization and regeneration

Why it matters:

- these are core completion gates, not optional reporting extras

### 7. Session ambiguity and duplicate ownership resolution

Recovery semantics cover this, but the operator-facing action path still feels more appendix-level than product-level.

Needed:

- explicit session conflict inspection
- explicit choose-authoritative-session / invalidate-session path
- safe pause on ambiguous ownership

Why it matters:

- long-running tmux-backed sessions will hit duplicate or stale session scenarios

### 8. Policy/config edits as a normal product flow

Project policy changes are called out, but the common journey for editing policies and seeing the downstream effect is not fully productized.

Needed:

- explicit policy update surface
- diff/preview of workflow changes
- rebuild impact analysis

Why it matters:

- this system is defined by YAML and policy; changing policy is not an edge case

### 9. Partial child completion and optional-child semantics

The docs default to “all current layout children must complete,” but real use may require optional, deferred, or replaced children.

Needed:

- explicit required-vs-optional child semantics
- parent completion rule clarity when some children are advisory, experimental, or abandoned

Why it matters:

- otherwise the scheduler/finalizer will be overly rigid for real project work

### 10. Human approval and intervention loops

Pause/gating exists, but the human journey after a pause still needs stronger modeling.

Needed:

- inspect active gate
- approve/reject/modify path
- resumption semantics after human intervention

Why it matters:

- approval gates are central to keeping automated mutation safe

---

## Highest-priority gaps to close before implementation

If the goal is to support the most common real user journeys reliably, the highest-value remaining design closures are:

1. blocker and pause-state introspection
2. compile-failure inspection and retry flow
3. child materialization/scheduling finalization
4. manual-vs-auto reconciliation commands and authority model
5. old-version active-run handling during supersession
6. impossible-wait/dependency diagnosis surfaces
7. review/testing execution and persistence semantics
8. explicit human gate/intervention flow

---

## Bottom line

The notes already cover the core product loop well:

- create work
- decompose it
- run it
- inspect it
- recover it
- rebuild it
- merge it
- explain it

The biggest remaining risk is not lack of broad capability. It is lack of precision in the operational journeys around:

- blocked work
- hybrid structures
- failed compilation
- superseded live work
- ambiguous recovery

Those are the places where real users will decide whether the system feels reliable or fragile.
