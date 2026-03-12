# Incremental Parent Merge For Sibling Dependencies

## Goal

Define the authoritative implementation direction for daemon-owned incremental child-to-parent merging so sibling dependencies only unblock after prerequisite sibling work is durably merged into the parent lineage they will clone from.

## Rationale

- Rationale: The current lifecycle-only sibling dependency model lets dependent children start from stale parent state, which breaks the intended meaning of sibling prerequisites whenever one child must actually see another child’s work.
- Reason for existence: This overview exists to lock the runtime doctrine, durable-state model, module boundaries, prompt/context expectations, and proving strategy before the repo implements the incremental merge lane across database, daemon, CLI inspection, and later E2E coverage.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `notes/planning/implementation/dependency_graph_and_admission_control_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`

## Scope

- Database: define and stage durable per-parent merge-lane state, per-child incremental merge state, applied merge order audit, and lineage-safe supersession behavior.
- CLI: define which existing operator inspection surfaces must expose blocker, merge, conflict, and reconcile truth for incremental parent merge flows.
- Daemon: define and then implement the background scan, per-parent lock, merge execution, dependency unblock, refresh, and conflict handoff behavior.
- YAML: no new live coordination authority moves into YAML; any policy fields must remain declarative and respect the code-vs-YAML boundary.
- Prompts: define daemon-assembled child startup, parent conflict, and final reconcile prompt/context payloads for incremental merge-aware runtime behavior.
- Tests: define bounded, integration, and full real E2E proof for completion-driven incremental merges, restart safety, conflict handling, and final reconcile semantics.
- Performance: keep the scan-and-lock merge lane cheap enough for repeated daemon polling and operator inspection without broad rescans or unstable query cost.
- Notes: update the runtime, git, lifecycle, database, CLI, and parent/child doctrinal notes so the repo’s implementation claims match the accepted incremental merge model.

## Purpose

Capture the code-backed plan for fixing the current sibling-dependency flow gap where dependent children can unblock without ever seeing the prerequisite sibling's merged parent state.

It is not an implementation claim.

## Confirmed Current Behavior

The current runtime has four separate pieces that do not yet connect into the needed flow.

### 1. Dependency readiness is lifecycle-based, not parent-state-based

- `src/aicoding/daemon/admission.py` clears a sibling dependency when the target sibling reaches the required lifecycle state, currently `COMPLETE`.
- That makes the dependent sibling startable, but it does not prove the parent branch or parent-visible context has incorporated the prerequisite sibling's output.

### 2. Auto child scheduling only starts children

- `src/aicoding/daemon/session_records.py` in `auto_bind_ready_child_runs(...)` checks dependency readiness and then admits/binds ready children.
- That loop has no incremental merge or re-bootstrap step between "dependency satisfied" and "start dependent sibling."

### 3. Child repos inherit parent ancestry only at bootstrap time

- `src/aicoding/daemon/live_git.py` bootstraps child repos by cloning from the parent/base repo and checking out the seed/base commit.
- If the parent repo has not absorbed the prerequisite sibling's work yet, later siblings still begin from stale ancestry.

### 4. Child merge is currently a later parent-local stage

- `src/aicoding/daemon/child_reconcile.py` and `src/aicoding/daemon/live_git.py` expose merge/reconcile only as an explicit parent merge path.
- The repository already declares `auto_merge_to_parent` in node/runtime policy, but no daemon path currently consumes that policy as part of dependency unblocking.

## Problem Statement

For a sibling dependency chain such as `A -> B`:

1. child `A` runs from the parent's current state
2. child `A` finishes
3. child `B` becomes "ready" because `A` is `COMPLETE`
4. child `B` still clones or continues from the pre-merge parent state

That breaks the intended dependency meaning whenever `B` is supposed to build on files, docs, summaries, or git state produced by `A`.

## Clarified Assumptions From Review

These assumptions are now explicit for this future-plan bundle.

- A child is mergeable upward when the child is done running, has no more subtasks to execute, and is ready to go as a completed child result.
- Child work is not optional with respect to upward visibility. Every child must eventually merge upward into its parent or that child work is lost.
- A dependent child is not truly `ready` when a prerequisite sibling merely reaches `COMPLETE`; it is `ready` only after all prerequisite siblings have been successfully merged into the parent.
- A dependency-unblocked child should wait until that merge finishes before it clones or refreshes git state from the parent.
- Incremental merge should not be a conditional "maybe merge if needed" decision inside the child scheduler. The system should update parent state after every child completes, and dependency unblock should happen only after that merge finishes.

## Notes Reviewed In This Pass

The additional note review materially changed the shape of this plan.

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/modules/wait_for_child_completion.md`
- `notes/pseudocode/modules/collect_child_results.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `notes/pseudocode/state_machines/node_lifecycle.md`
- `notes/pseudocode/pseudotests/orchestration_and_state_tests.md`

## Spec Tension Discovered

The current notes mostly describe this parent flow:

1. materialize children
2. schedule children
3. wait for children
4. collect child results
5. reconcile parent

That doctrinal flow appears in:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/pseudocode/modules/wait_for_child_completion.md`
- `notes/pseudocode/modules/collect_child_results.md`

That model is not sufficient for sibling-dependent children that must start from merged parent state. The repo therefore needs a revised runtime model, not only an implementation patch.

## Required Runtime Contract

When a child finishes and another sibling depends on it, the daemon must decide whether that completed child has to be merged back into parent state before the dependent sibling can run.

Required contract:

- dependency unblocking must consider whether the prerequisite child is merged into the parent, not only whether the child lifecycle is `COMPLETE`
- the merge must be daemon-owned, durable, idempotent, and inspectable
- the dependent sibling must start from parent state that already includes the prerequisite child's accepted contribution
- the later full `wait_for_children` plus `reconcile_children` stage must still exist for the final all-children parent pass

Refined contract from this review:

- parent state must advance after every completed child, not only at the end
- dependency unblock must happen after merge completion, not before
- child bootstrap from parent must happen only against the latest accepted parent head for that child's prerequisite set
- the later final reconcile stage is still required, but it becomes "final parent synthesis after incremental child merges," not "first time child output reaches the parent"

Additional contract decisions from later review:

- incremental merges should happen in daemon-observed child completion order
- no precomputed deterministic sibling merge sequence is required for incremental merge processing
- each successful incremental merge should record its actual `applied_merge_order`
- if multiple completed children are discovered in the same scan window, the daemon may choose any one of them; only the actual applied order must be persisted durably

## Proposed Design

### Phase 1: Add a parent incremental-merge monitor loop

The daemon needs a dedicated parent-owned loop that is separate from:

- child run admission
- child session binding
- final parent reconcile

The loop should watch authoritative child completion and immediately reconcile parent git/runtime state forward one child at a time.

This loop likely belongs adjacent to the current child auto-start loop in:

- `src/aicoding/daemon/session_records.py`

but should be implemented as a distinct daemon-owned path rather than folded into `auto_bind_ready_child_runs(...)`.

This should follow the repo's existing daemon-owned background-scan model rather than a separate queue/claim worker model:

- scan authoritative durable state for completed-unmerged children
- take a per-parent advisory lock
- re-check state inside the lock
- process at most one incremental merge step for that parent
- persist the result and release the lock

### Phase 2: Introduce explicit incremental merge state

Add a daemon-owned concept equivalent to:

- `ready_for_incremental_parent_merge`
- `incremental_parent_merge_in_progress`
- `merged_for_sibling_dependents`
- `incremental_merge_conflicted`
- `dependent_children_refresh_required`

The exact storage shape can vary, but the runtime needs a durable way to know:

- which child finals were already merged into the parent for dependency-unblock purposes
- which merge head or parent commit they produced
- whether the merge was clean, conflicted, superseded, or invalidated by later parent changes
- whether blocked dependents have already been refreshed against that new parent state

### Phase 3: Change dependency-unblock semantics

For sibling dependencies:

- do not treat child completion alone as sufficient
- require every prerequisite sibling to reach a merge-backed satisfied state before admitting the dependent child

This likely means either:

- expanding dependency blocker evaluation in `src/aicoding/daemon/admission.py`, or
- introducing a second daemon-owned blocker layer that is checked alongside lifecycle readiness

The likely first insertion point is:

- `src/aicoding/daemon/admission.py`

because that is where "ready versus blocked" currently collapses too early.

### Phase 4: Add an incremental merge executor

The daemon should run a narrow merge-to-parent step when:

- child `A` has a mergeable final commit
- one or more siblings exist, regardless of whether they are currently ready to start
- the child has not already been incrementally merged upward for the current authoritative parent state

Expected behavior:

- merge `A` into the parent live repo or parent version working state
- record durable merge audit rows
- persist the new parent head/state needed for later child bootstrap or resume
- expose conflicts and pause/escalation surfaces if the merge fails

Primary likely code locations:

- `src/aicoding/daemon/live_git.py`
- `src/aicoding/daemon/child_reconcile.py`

The live git layer should own actual git mutation.
The reconcile layer should own ordering, audit context, and parent-visible merge status.

### Phase 5: Refresh dependent-child bootstrap against the new parent

When child `B` becomes unblocked after `A` merges:

- a not-yet-started child `B` should bootstrap from the updated parent state
- an already-bootstrapped but still blocked child `B` likely needs a daemon-owned reset/re-bootstrap/rebase decision before admission

This phase needs an explicit invariant:

- a child that depends on sibling-produced parent state must never start from a parent ancestor older than the accepted incremental merges it depends on

Likely code locations:

- `src/aicoding/daemon/live_git.py`
- `src/aicoding/daemon/session_records.py`
- possibly `src/aicoding/daemon/materialization.py` if child bootstrap metadata must be refreshed there

### Phase 6: Separate incremental merge from final reconcile

Keep both layers:

- incremental merge-to-parent for dependency visibility between siblings
- final parent reconcile after all required children finish

The final reconcile stage still owns:

- all-children rollup logic
- final parent-local synthesis
- later review/testing/docs/finalize flow

## Proposed Daemon Loop Lifecycle

The current repo does not yet define this lifecycle, so it needs to be added explicitly.

### Parent-side loop states

Suggested parent runtime progression:

1. `RUNNING`
2. `WAITING_ON_CHILDREN`
3. `INCREMENTAL_MERGE_PENDING`
4. `INCREMENTAL_MERGE_RUNNING`
5. `WAITING_ON_CHILDREN`
6. repeat until all required children merged upward
7. `READY_FOR_FINAL_RECONCILE`
8. existing reconcile/quality/finalize path

Whether those become formal lifecycle states or run-state/cursor states is still open, but the semantics need to exist durably.

### Child-side dependency lifecycle

Suggested child-side blocked progression:

1. `READY`
2. `WAITING_ON_SIBLING_DEPENDENCY`
3. `WAITING_ON_SIBLING_INCREMENTAL_MERGE`
4. `WAITING_ON_PARENT_REFRESH`
5. `READY`
6. `RUNNING`

This is the current missing semantic ladder.

## Ownership Boundary

This future design should distinguish daemon-owned orchestration from AI-session-owned work very explicitly.

### Daemon-owned happy-path responsibilities

- detect child completion
- make completed-unmerged child merge state durably discoverable
- merge completed child into parent state
- persist merge audit and resulting parent head/state
- refresh blocked-child dependency truth
- mark newly satisfied children `READY`
- auto-start newly ready children when policy allows

### Parent AI-session responsibilities

- no action on ordinary successful incremental merges
- inspect progress if asked
- continue normal parent-local work only after all required children are merged upward

### Parent AI-session exceptional responsibilities

- handle merge conflicts that require semantic resolution
- handle ambiguity or policy-driven pause cases
- perform the later final parent reconcile / review / testing / docs / finalize work

This means the incremental merge path should be a daemon runtime pathway, not a separate AI worker loop.

## Happy-Path Flowchart

The normal success path should look like this.

```text
child node run finishes successfully
-> daemon records child COMPLETE + final commit + summary
-> daemon finds parent for that child
-> durable state now shows "completed child not yet merged upward"

background parent incremental-merge loop wakes
-> scan authoritative parents/children from durable state
-> choose a parent with completed-unmerged children
-> acquire parent merge lock
-> re-load parent authority + current parent merge state inside the lock
-> choose the next completed-unmerged child in daemon-observed completion order
-> verify child is still authoritative and mergeable
-> execute child merge into parent live repo/state
-> persist merge event + resulting parent head/state + applied incremental merge order
-> mark child incrementally merged
-> update blocked dependent-child refresh state
-> recompute dependency blockers for affected siblings
-> any child whose prerequisite siblings are all incrementally merged becomes READY
-> release parent merge lock

existing child auto-start loop observes READY children
-> admit newly ready child runs
-> bootstrap/bind child sessions from updated parent state

when all required children are complete and incrementally merged
-> parent enters final reconcile-ready state
-> parent AI session performs final parent-local synthesis and downstream quality/finalize stages
```

## Conflict-Path Flowchart

The exceptional path should escalate to the parent AI session only when daemon-owned merge execution cannot safely continue.

```text
child node run finishes successfully
-> daemon records child COMPLETE + final commit + summary
-> durable state now shows "completed child not yet merged upward"

background parent incremental-merge loop wakes
-> scan authoritative state for a parent with completed-unmerged children
-> acquire parent merge lock
-> load next completed-unmerged child in daemon-observed completion order
-> attempt child merge into parent
-> merge conflict occurs
-> persist merge conflict row + workflow event + blocked incremental-merge state
-> keep dependent siblings blocked
-> expose conflict in parent inspection/context surfaces
-> release parent merge lock

parent AI session is notified through durable context / prompt surface
-> inspect conflict
-> resolve semantic/code conflict as required
-> report resolution / complete reconcile-conflict path

daemon resumes incremental merge processing
-> revalidate parent state after conflict resolution
-> mark child incrementally merged when successful
-> recompute dependent-child readiness
-> unblock/start dependents only after merge success is durable
```

## Refined Full Workflow

Putting the ownership and flow together:

### Normal path

1. child AI session finishes child node work
2. daemon marks child complete
3. daemon incrementally merges child upward into parent
4. daemon updates dependency truth
5. daemon allows dependent siblings to clone/start from updated parent state
6. daemon repeats this for every completed child
7. parent AI session only becomes active again for final reconcile after all required children are complete and merged

### Exceptional path

1. child AI session finishes child node work
2. daemon attempts incremental merge
3. merge conflict or unsafe condition occurs
4. daemon pauses/blocks this parent incremental-merge lane
5. parent AI session handles conflict/reconcile work
6. daemon resumes incremental merge processing after the resolution is durable

## Merge Ordering Contract

Incremental merge ordering should be defined narrowly.

- The daemon should merge completed children upward in the order it observes and applies them during live runtime.
- The system should not require a precomputed deterministic sibling merge sequence for incremental merge processing.
- The runtime must persist the actual `applied_merge_order` for every successful incremental child merge.
- Final parent reconcile must consume the recorded applied incremental merge history rather than recomputing a different sibling merge order.
- If multiple completed children are discovered in the same scan window, the daemon may choose any one of them; correctness depends on persisting the actual applied order, not on choosing a deterministic tie-break rule.

## Concrete Backend Path Sketch

This is the current best guess for code ownership.

### Child completion hook

- `src/aicoding/daemon/run_orchestration.py`

Needed behavior:

- when a child run becomes successful terminal completion, record enough durable state that the background parent loop can discover a completed-unmerged child during its next scan

### Parent incremental merge loop

- likely new module: `src/aicoding/daemon/incremental_parent_merge.py`
- invoked from the daemon background/runtime layer, not from CLI-only commands

Needed behavior:

- scan for completed-unmerged child results
- serialize parent merge authority
- run incremental merges
- update parent merge progress and child-ready states

### Dependency-truth update

- `src/aicoding/daemon/admission.py`

Needed behavior:

- stop treating `COMPLETE` alone as dependency satisfaction
- require prerequisite siblings to be incrementally merged into parent state

### Git mutation and conflict capture

- `src/aicoding/daemon/live_git.py`
- `src/aicoding/daemon/child_reconcile.py`

Needed behavior:

- perform merge
- record merge event/conflict
- persist resulting parent head

### Existing child auto-start loop remains narrower

- `src/aicoding/daemon/session_records.py`

Its job after redesign:

- only start children already marked `READY`
- do not decide incremental merge policy
- do not bypass parent merge-backed dependency truth

## Testing Matrix Expansion

### Bounded / mock-oriented proof

- child completion creates durable incremental-merge work
- parent incremental-merge loop processes one completed child exactly once
- dependent child remains blocked until merge success is durable
- successful merge flips dependent child from blocked to ready
- duplicate loop wakeups do not double-merge the same child
- conflict path records durable blocked/conflict state
- restart between child completion and merge processing is idempotent
- restart between merge success and dependent-child admission preserves correct readiness

### Real E2E proof

- child A completes and is incrementally merged upward without parent AI intervention
- dependent child B starts only after the merged parent state is available
- B clones/executes against the updated parent content
- conflict path blocks B and routes to parent AI conflict handling
- after conflict resolution, daemon resumes and B unblocks correctly

## Prompt Formation Model

The incremental-merge redesign also changes how daemon-owned prompt context should be formed.

Core rule:

- prompts should remain daemon-assembled from durable runtime truth
- AI sessions should not reconstruct sibling-merge visibility by scraping prior terminal output
- incremental merge state should be delivered through structured stage context

### Child startup prompt formation

When a dependent child starts, the daemon should build its prompt/context from:

- the compiled child subtask prompt
- current node/run/startup metadata
- the exact parent head commit or parent merge generation the child is starting from
- the list of prerequisite sibling merges already incorporated into that parent state
- any remaining blocked prerequisites, if start is still not legal

Suggested context shape:

```text
stage_context_json = {
  startup: ...,
  parent_git_state: {
    parent_node_id,
    parent_node_version_id,
    parent_head_commit_sha,
    parent_merge_generation,
  },
  dependency_merge_state: {
    required_sibling_merges: [...],
    satisfied_sibling_merges: [...],
    blocked_sibling_merges: [...],
  },
  history: ...,
}
```

Prompt consequence:

- the child AI should be told which sibling-produced parent updates are already present
- the child AI should not assume visibility of sibling work that is not listed in that startup context

### Parent prompt formation during ordinary incremental merge success

No ordinary AI prompt should be required during successful incremental child merges.

Instead, the daemon should persist incremental merge state so that later parent inspection or prompt retrieval can see:

- which children completed
- which were merged upward already
- parent head/state after each merge
- which dependent siblings were unblocked as a result

This belongs in durable history and stage context, not in repeated active prompts to the parent AI session.

### Parent prompt formation during incremental merge conflict

If the daemon hits a merge conflict, then the parent AI session does need a daemon-built prompt.

That prompt/context should include:

- parent commit before the failed merge
- child being merged
- child final commit
- conflicted files
- already-applied incremental merges
- currently blocked dependent siblings waiting on this merge

Suggested context shape:

```text
stage_context_json = {
  startup: ...,
  incremental_merge_conflict: {
    child_node_id,
    child_node_version_id,
    child_final_commit_sha,
    parent_commit_before,
    conflicted_files,
    applied_prior_child_merges: [...],
    blocked_dependents: [...],
  },
  history: ...,
}
```

Prompt consequence:

- the parent AI gets a focused conflict-resolution prompt rather than a vague "reconcile parent" prompt
- the AI has enough daemon-supplied context to resolve the conflict without reconstructing orchestration state manually

### Final parent reconcile prompt formation

After all required children are complete and incrementally merged upward, the final parent reconcile prompt changes meaning.

It should no longer mean:

- merge children into parent now

It should instead mean:

- all required child merges are already applied
- perform the remaining parent-local synthesis, summary reconciliation, and downstream quality/finalize work

Suggested context shape:

```text
stage_context_json = {
  startup: ...,
  merged_child_history: {
    merged_children_in_order: [...],
    current_parent_head_commit_sha,
    merge_conflicts_resolved: [...],
  },
  child_results: {
    summaries: [...],
    final_outputs: [...],
  },
  remaining_parent_obligations: {
    reconcile,
    validate,
    review,
    test,
    docs,
    finalize,
  },
}
```

### Likely code touchpoints for prompt assembly

- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/child_reconcile.py`

Most likely impact:

- extend `stage_context_json` assembly to include incremental-merge and parent-git-state fields
- keep prompt templates relatively stable while making the daemon context much richer

## Pause And Cancel Contract

Pause and cancel should stop forward progression without erasing already-written audit history.

### Parent paused

- the parent incremental merge lane must stop processing new child merges
- completed-unmerged child state remains durable
- dependent children remain blocked until the parent resumes and the merge lane can continue

### Child paused before completion

- the child is not eligible for incremental merge
- dependents remain blocked on ordinary dependency completion truth

### Child failed or cancelled before completion

- the child is not eligible for incremental merge
- dependents move to the existing impossible/block/failure path rather than waiting on incremental merge

### Child cancelled after successful completion

- cancellation should not erase a durably recorded completed child final by itself
- only supersession/regeneration or another explicit lineage-invalidating action should make that completed child final ineligible

### Parent cancelled

- stop parent incremental merge processing
- do not auto-admit dependent children
- preserve already-written merge history and blocker history

### Conflict pause

- if an incremental merge conflicts, the lane enters conflicted/paused state
- dependents remain blocked on incremental merge conflict
- once the conflicted parent repo is manually resolved and committed, the existing durable `resolve_conflict` path should advance the affected incremental child merge row and parent lane to that resolved head before dependents can unblock
- parent AI or operator resolution is required before the lane resumes

## Durable State Model

This future design needs explicit durable state. Without it, the daemon cannot recover safely across restart, retry, conflict, or repeated loop wakeups.

### Core persistence requirement

The daemon must be able to answer all of these from durable state alone:

- which completed children still need incremental merge
- which children were already incrementally merged upward
- what parent head/state resulted from each incremental merge
- which dependent children are still blocked on sibling incremental merge
- which dependent children were bootstrapped from stale parent state and must refresh before admission
- whether a parent incremental merge lane is currently conflicted or paused

### Minimum conceptual records

Even if the final schema uses different names, the runtime needs durable equivalents of the following record types.

#### 1. Incremental child merge state

One durable record per parent-child incremental merge lane:

```text
incremental_child_merge_state = {
  parent_node_version_id,
  child_node_version_id,
  child_final_commit_sha,
  status,  # completed_unmerged | running | merged | conflicted | superseded | invalid
  applied_merge_order?,
  parent_commit_before,
  parent_commit_after,
  conflict_id?,
  created_at,
  updated_at,
}
```

Purpose:

- prevents double-merging the same completed child
- lets the daemon resume after restart by rescanning durable state
- gives operator/AI surfaces a stable view of merge progress and actual applied merge order

#### 2. Parent incremental merge lane state

One durable record per parent lane:

```text
parent_incremental_merge_lane = {
  parent_node_version_id,
  status,  # idle | pending | running | conflicted | paused | complete_for_now
  current_parent_head_commit_sha,
  last_successful_merge_at,
  blocked_reason?,
  updated_at,
}
```

Purpose:

- gives the daemon one authority row to lock/serialize
- prevents multiple background workers from mutating the same parent at once
- exposes whether the parent is presently merge-blocked or simply waiting for more child completions

#### 3. Dependent child refresh state

One durable row or per-child state payload:

```text
dependent_child_refresh_state = {
  child_node_version_id,
  parent_node_version_id,
  bootstrapped_from_parent_commit_sha?,
  required_parent_commit_sha?,
  refresh_status,  # current | refresh_required | refreshing | refreshed | invalid
  updated_at,
}
```

Purpose:

- proves whether a blocked child was prepared from stale parent ancestry
- allows the daemon to prevent admission until the child is aligned with the merged parent state it depends on

#### 4. Expanded dependency blocker truth

The current blocker model already exists, but it needs richer blocker kinds.

At minimum the daemon needs blocker kinds equivalent to:

- `blocked_on_dependency`
- `blocked_on_incremental_merge`
- `blocked_on_parent_refresh`
- `blocked_on_incremental_merge_conflict`

Purpose:

- makes the child blocked reason inspectable
- prevents the current incorrect collapse of "dependency sibling is COMPLETE, therefore child is ready"

### Likely schema directions

The existing tables and records that likely need extension or adjacent companions are:

- `node_dependencies`
- `node_dependency_blockers`
- `parent_child_authority`
- existing merge event / merge conflict records
- node lifecycle or run cursor state for parent-side temporary loop progress

The current notes do not yet define a dedicated incremental-merge table family, so that will need to be designed explicitly when this moves out of future planning.

### Invariants the durable model must enforce

#### Invariant 1

- a child final commit must not be incrementally merged upward more than once for the same authoritative parent baseline unless an explicit reset/replay event invalidated prior merge state

#### Invariant 2

- a dependent child must not be admitted when `required_parent_commit_sha` is newer than `bootstrapped_from_parent_commit_sha`

#### Invariant 3

- dependency satisfaction for sibling-blocked children must be computed from incremental-merge state, not only child lifecycle state

#### Invariant 4

- a conflicted parent incremental-merge lane must keep affected dependents blocked until the conflict is durably resolved

#### Invariant 5

- after daemon restart, replaying the parent loop from durable rows must produce the same merge/unblock decisions as before the restart

## Supersession And Cutover Contract

Incremental merge truth must stay aligned with authoritative lineage selection.

- dependency truth should continue to resolve against authoritative node versions, not stale candidate versions
- if a child is superseded before its completed final is incrementally merged, the old child should not be merged upward into the current authoritative parent lineage
- if a parent version is superseded before a completed child is incrementally merged upward, the old parent lineage should not continue receiving new incremental merges
- merges already applied to an old lineage remain valid audit history for that lineage, but they do not automatically transfer to a new authoritative lineage
- dependents should unblock only from merges applied to the authoritative parent lineage they will actually bootstrap from
- superseded or invalidated incremental merge state should remain inspectable as historical truth rather than being silently discarded

### Likely implementation layering

The durable state probably divides into two categories:

#### Long-lived audit/history

- merge events
- merge conflicts
- parent head transitions
- child-to-parent merge lineage

#### Live coordination state

- which merges are pending/running
- whether the parent merge lane is currently conflicted
- whether a child refresh is required before admission

The first category is historical/audit-oriented.
The second category is orchestration-oriented.
Both are required.

### Bounded tests required for the durable model

- child completion writes one completed-unmerged incremental-merge state row
- repeated loop scans do not create duplicate merge state
- successful merge flips completed_unmerged/running -> merged and records parent commit transition plus applied merge order
- conflicted merge flips completed_unmerged/running -> conflicted and keeps dependents blocked
- dependent child with stale bootstrap commit is not admitted
- restart-safe replay preserves merge state and child refresh truth

## Lifecycle And State Vocabulary

The current repo already has lifecycle states, run-state/cursor fields, and blocker rows.
This future design should use those layers deliberately rather than forcing every new concept into one status field.

### Recommended split

Use three layers:

1. node lifecycle states for major operator-visible execution phases
2. run cursor / live coordination state for fine-grained daemon progress
3. dependency blocker kinds for why a child is still not startable

### 1. Formal lifecycle states

These are the states most likely worth exposing as true node lifecycle values.

#### Parent lifecycle

Recommended parent additions:

- `INCREMENTAL_MERGE_PENDING`
- `INCREMENTAL_MERGE_RUNNING`
- `READY_FOR_FINAL_RECONCILE`

Meaning:

- `INCREMENTAL_MERGE_PENDING`: at least one completed child still needs merge-up processing
- `INCREMENTAL_MERGE_RUNNING`: the daemon currently owns a live incremental merge step for this parent
- `READY_FOR_FINAL_RECONCILE`: all required children are complete and already merged upward; parent-local final synthesis can begin

These states fit the existing lifecycle model better than hiding the whole parent loop in invisible cursor data.

#### Child lifecycle

Recommended child addition:

- keep `WAITING_ON_SIBLING_DEPENDENCY`

Do not rush to add a large number of extra child lifecycle states unless operator visibility truly needs them.
The child is still fundamentally "waiting on sibling dependency"; the finer reason can live in blocker rows and refresh state.

### 2. Run cursor / live coordination state

These concepts are likely too fine-grained or transient for top-level lifecycle values and should live in parent run state, coordination rows, or execution cursor data.

Recommended cursor/coordination values:

- `incremental_merge.current_child_node_version_id`
- `incremental_merge.current_status`
- `incremental_merge.parent_commit_before`
- `incremental_merge.parent_commit_after`
- `incremental_merge.pending_child_count`
- `incremental_merge.last_merged_child_node_version_id`
- `incremental_merge.last_successful_merge_at`

Recommended lane/worker values:

- `idle`
- `pending`
- `running`
- `conflicted`
- `paused`
- `complete_for_now`

Reason:

- these values describe daemon work-in-progress and background-scan coordination
- they change more often than node lifecycle should
- they are still critical for recovery and operator inspection

### 3. Dependency blocker kinds

The child blocked reason should primarily expand through blocker kinds.

Recommended blocker vocabulary:

- `blocked_on_dependency`
- `blocked_on_incremental_merge`
- `blocked_on_parent_refresh`
- `blocked_on_incremental_merge_conflict`
- `impossible_wait`
- `invalid_authority`

Meaning:

- `blocked_on_dependency`: prerequisite sibling is not yet complete
- `blocked_on_incremental_merge`: prerequisite sibling is complete but not yet merged upward
- `blocked_on_parent_refresh`: child bootstrap/worktree is stale relative to required parent head
- `blocked_on_incremental_merge_conflict`: prerequisite merge hit a conflict and cannot yet unblock dependents

This is likely the most important operator-facing distinction for child readiness.

## Recommended State Progressions

### Parent progression

Suggested high-level parent path:

```text
RUNNING
-> WAITING_ON_CHILDREN
-> INCREMENTAL_MERGE_PENDING
-> INCREMENTAL_MERGE_RUNNING
-> WAITING_ON_CHILDREN
-> repeat until all required children are merged upward
-> READY_FOR_FINAL_RECONCILE
-> VALIDATION_PENDING / REVIEW_PENDING / TESTING_PENDING / ...
-> COMPLETE
```

### Child progression

Suggested child path:

```text
READY
-> WAITING_ON_SIBLING_DEPENDENCY
-> READY
-> RUNNING
```

With blocker-detail progression underneath:

```text
blocked_on_dependency
-> blocked_on_incremental_merge
-> blocked_on_parent_refresh
-> no blockers
```

This keeps the top-level child lifecycle relatively stable while still exposing the real reason the child cannot yet start.

## Why This Split Is Better

If every new merge concept becomes a top-level lifecycle state:

- the lifecycle model becomes noisy and hard to reason about
- state-transition legality becomes harder to maintain
- transient daemon work looks like durable business-state changes

If everything stays hidden in cursor data:

- operators cannot inspect the orchestration truth
- tests cannot cleanly assert the runtime contract
- recovery reasoning gets too implicit

The three-layer split gives:

- lifecycle for major visible phases
- coordination state for daemon work-in-progress
- blocker kinds for child admission truth

## Open State Questions

- whether `READY_FOR_FINAL_RECONCILE` should be a full lifecycle state or just a parent run-state marker
- whether `INCREMENTAL_MERGE_PENDING` is necessary as a lifecycle state if `WAITING_ON_CHILDREN` plus lane state already exposes enough detail
- whether child-side `WAITING_ON_PARENT_REFRESH` ever deserves promotion from blocker kind to lifecycle state
- whether parent merge-lane state belongs in `node_run_state.execution_cursor_json` first or deserves its own table immediately

## Tests Required For Vocabulary

- lifecycle transitions remain legal and restart-safe with the new parent states
- child admission distinguishes blocker kinds correctly without overloading lifecycle values
- operator inspection surfaces show both lifecycle and blocker truth without contradiction
- daemon restart preserves lane state and blocker state consistently

## Daemon Module Boundaries

This future design is large enough that it should not be implemented by smearing new logic across unrelated runtime files.

The backend should be split by responsibility.

### Recommended module ownership

#### `src/aicoding/daemon/run_orchestration.py`

Keep ownership of:

- node run advancement
- subtask completion
- terminal child success detection
- emitting durable "incremental merge required" work when a child run completes successfully

Do not make this module own:

- background scanning of all parents
- live git merge execution
- dependency-blocker recomputation policy

Reason:

- this module already owns immediate run lifecycle transitions
- it should emit the parent-work signal, not become the whole parent orchestration engine

#### New module: `src/aicoding/daemon/incremental_parent_merge.py`

Recommended new ownership:

- scanning for parents with completed-unmerged children
- parent merge-lane locking/serialization
- choosing next child to merge in daemon-observed completion order
- coordinating one child-at-a-time incremental merge execution
- writing parent merge-lane state
- triggering dependent-child refresh/reblock/unblock recomputation

Reason:

- this is the new core runtime concept
- it is substantial enough to deserve its own module and tests
- it is a daemon pathway, not a CLI convenience wrapper

Likely exported entry points:

```text
process_pending_incremental_parent_merges(...)
process_parent_incremental_merge(...)
select_next_completed_unmerged_child(...)
mark_incremental_merge_conflicted(...)
resume_parent_incremental_merge_after_resolution(...)
```

#### `src/aicoding/daemon/admission.py`

Keep ownership of:

- dependency readiness classification
- child blocked-vs-ready decisions
- blocker persistence

Required changes:

- stop treating sibling `COMPLETE` alone as satisfaction
- incorporate incremental merge state and refresh state into readiness truth
- expose richer blocker kinds to operator and CLI surfaces

Reason:

- this remains the authoritative "can the node start now?" boundary

#### `src/aicoding/daemon/live_git.py`

Keep ownership of:

- actual git mutation
- parent/child repo bootstrap and refresh mechanics
- merge execution
- merge conflict capture
- resulting parent head lookup/persistence hooks

Required changes:

- support incremental one-child merge execution as a first-class path
- support child refresh/bootstrap against newer parent state before admission

Reason:

- git mutation safety belongs here, not in admission or generic background code

#### `src/aicoding/daemon/child_reconcile.py`

Keep ownership of:

- actual applied child merge order reporting
- parent-visible merge/reconcile snapshots
- merge-event context assembly
- final parent reconcile readiness/read models

Required changes:

- distinguish "incrementally merged upward already" from "ready for later final reconcile"
- expose merged-upward child history separately from not-yet-merged completed children

Reason:

- this module is already the best fit for parent-facing merge state views

#### `src/aicoding/daemon/session_records.py`

Keep ownership of:

- background child auto-start loop
- session bind/start for already-ready children

Required changes:

- narrow the loop so it only starts children already marked `READY`
- do not let this module decide merge policy
- optionally call the new parent incremental-merge processor in the same background scheduler, but not implement the merge logic inline

Reason:

- this module already contains background runtime helpers
- it should remain a scheduler/launcher surface, not the source of dependency truth

#### `src/aicoding/daemon/operator_views.py` and `src/aicoding/daemon/app.py`

Keep ownership of:

- operator-facing inspection endpoints and response shapes

Required changes:

- expose parent incremental merge lane state
- expose richer dependency blocker reasons
- expose whether blocked children require parent refresh

Reason:

- this feature is not implemented unless operators can inspect and explain it

## Canonical CLI Proving Surface

This feature should reuse the repo's existing inspection surfaces before introducing a new command family.

Primary reads to extend and rely on:

- `python3 -m aicoding.cli.main node blockers --node <id>`
- `python3 -m aicoding.cli.main node dependency-status --node <id>`
- `python3 -m aicoding.cli.main node child-results --node <id>`
- `python3 -m aicoding.cli.main node reconcile --node <id>`
- `python3 -m aicoding.cli.main git merge-events show --node <id>`
- `python3 -m aicoding.cli.main git merge-conflicts show --node <id>`

Expected responsibilities:

- `node blockers`
  - current blocker kind, including `blocked_on_incremental_merge`, `blocked_on_parent_refresh`, and `blocked_on_incremental_merge_conflict`
- `node dependency-status`
  - overall readiness as derived from merge-backed truth
- `node child-results`
  - completed children
  - incrementally merged children
  - actual `applied_merge_order`
  - blocked-child classification
- `node reconcile`
  - final parent reconcile readiness and merged-child context
- `git merge-events show`
  - durable incremental merge audit trail, including parent before/after commit and applied merge order
- `git merge-conflicts show`
  - unresolved conflict state and inspectable conflict metadata

Only add a new command such as `node merge-lane --node <id>` later if these existing surfaces become too overloaded in practice.

## Suggested End-To-End Internal Call Graph

The likely backend call chain should look like this.

```text
run_orchestration.py
-> child run reaches successful terminal completion
-> persist completed child final state

background daemon scheduler
-> incremental_parent_merge.process_pending_incremental_parent_merges()
-> incremental_parent_merge.process_parent_incremental_merge(parent)
-> incremental_parent_merge chooses next completed-unmerged child by completion order
-> live_git executes one incremental merge
-> admission recomputes blockers/readiness for affected dependents
-> session_records auto-start loop may then admit newly READY children
```

## What Should Not Happen

The design should avoid these implementation shapes.

### Bad shape 1

- all incremental merge logic stuffed into `session_records.py`

Why bad:

- mixes scheduling, session binding, dependency truth, and git mutation into one module

### Bad shape 2

- parent AI session told to poll and manually merge children during the happy path

Why bad:

- turns normal orchestration into prompt-driven babysitting
- loses restart-safe daemon ownership

### Bad shape 3

- dependency readiness patched ad hoc in `admission.py` without a durable parent merge lane model

Why bad:

- makes readiness depend on implicit or reconstructive logic
- breaks restart and operator inspection

### Bad shape 4

- final parent reconcile overloaded to also serve as the dependency-unblock merge path

Why bad:

- recreates the current flaw
- dependent children still cannot start from merged parent state in time

## Module-Level Testing Expectations

### `run_orchestration.py`

- bounded tests for child completion durable-state recording behavior

### `incremental_parent_merge.py`

- bounded tests for background scan processing, parent locking, idempotent replay, and conflict transitions
- integration tests for parent merge-lane behavior across real DB state

### `admission.py`

- bounded and integration tests for new blocker classification and readiness truth

### `live_git.py`

- bounded tests for one-child incremental merge and child refresh/bootstrap paths
- integration tests for conflict and post-merge parent-head persistence

### `session_records.py`

- integration tests proving the auto-start loop only starts children made ready by the merge-backed dependency path

## Staged Implementation Order

This should not be implemented as one large rewrite.

The safest path is a staged sequence where each phase introduces one new runtime contract and proves it before the next phase begins.

### Phase 1: Durable merge-lane scaffolding

Goal:

- create the durable parent incremental-merge state model
- make completed children discoverable by the background parent scan
- do not yet unblock dependents from it

Code focus:

- child completion hook in `run_orchestration.py`
- new durable merge-lane records / coordination model
- new `incremental_parent_merge.py` scaffolding

Proof required:

- bounded tests for durable-state discovery/idempotency
- integration tests that completed child runs create durable completed-unmerged incremental-merge state

Completion claim:

- `implemented`, not `verified` for the whole feature

### Phase 2: Daemon-owned one-child incremental merge

Goal:

- process one completed child into the parent live repo/state
- record parent head transition and merge audit
- still do not yet refresh/start dependents automatically

Code focus:

- `incremental_parent_merge.py`
- `live_git.py`
- `child_reconcile.py`

Proof required:

- bounded tests for one-child merge success, duplicate wakeup idempotency, and conflict recording
- integration tests for parent lane state transitions and parent commit persistence

Completion claim:

- `implemented` or `partial`

### Phase 3: Merge-backed dependency truth

Goal:

- change readiness semantics so sibling `COMPLETE` no longer unblocks children by itself
- dependents remain blocked until prerequisite siblings are incrementally merged upward

Code focus:

- `admission.py`
- blocker persistence / operator reads

Proof required:

- bounded tests for blocker transitions:
  - `blocked_on_dependency`
  - `blocked_on_incremental_merge`
  - `ready`
- integration tests proving a child is still blocked after sibling completion but before sibling merge success

Completion claim:

- `implemented` or `partial`

### Phase 4: Dependent-child parent refresh

Goal:

- ensure blocked dependents do not start from stale parent ancestry
- refresh or require fresh bootstrap against the current merged parent head before admission

Code focus:

- `live_git.py`
- `incremental_parent_merge.py`
- possibly `materialization.py` if bootstrap metadata needs persistence there

Proof required:

- bounded tests for stale-bootstrap detection
- integration tests for refresh-required vs current child state

Completion claim:

- `implemented` or `partial`

### Phase 5: Background orchestration wiring

Goal:

- wire the parent incremental-merge loop into the daemon background runtime
- keep child auto-start narrow: only start children already made ready by merge-backed truth

Code focus:

- daemon background runtime entry points
- `session_records.py`

Proof required:

- integration tests proving:
  - child completion triggers parent incremental merge processing
  - dependent child becomes ready only after merge success
  - auto-start loop starts the child only after readiness flips

Completion claim:

- `implemented`

### Phase 6: Conflict-handling prompt and parent AI handoff

Goal:

- when incremental merge conflicts, route to parent AI handling cleanly
- expose conflict context through prompt/context surfaces

Code focus:

- prompt context assembly
- conflict inspection surfaces
- parent-session resume/recovery hooks

Proof required:

- bounded tests for conflict context assembly
- integration tests for blocked dependents staying blocked during conflict state
- real conflict-path E2E once runtime is stable enough

Completion claim:

- `partial` until real conflict E2E exists

### Phase 7: Final parent reconcile semantics update

Goal:

- redefine final parent reconcile to mean "synthesize after incremental merges already applied"
- ensure no double-merge and no loss of parent-local finalization behavior

Code focus:

- `child_reconcile.py`
- final parent workflow stages
- prompt/context changes for final reconcile

Proof required:

- integration tests for merged-upward child history vs final reconcile-ready state
- real E2E proving final parent flow still completes after incremental merge path

Completion claim:

- `partial` or `verified` depending on E2E coverage

## Proving Slices

Each phase should have explicit bounded and real-runtime proof.

### Slice A: Durable state discovery

Bounded:

- completed child becomes discoverable once
- repeat scans are idempotent
- restart preserves completed-unmerged child merge truth

Real runtime:

- completed child creates durable pending merge work through real DB and daemon code path

### Slice B: One-child merge success

Bounded:

- parent merge lane transitions `pending -> running -> merged`
- resulting parent head is stored

Real runtime:

- child final commit is incrementally merged into parent repo through real git execution

### Slice C: Dependency gating

Bounded:

- child remains blocked after sibling completion but before merge success
- child becomes ready after merge success

Real runtime:

- dependent child cannot start until the prerequisite sibling is merged upward

### Slice D: Parent refresh correctness

Bounded:

- stale child bootstrap is detected
- child requires refresh before admission

Real runtime:

- dependent child starts from updated parent ancestry rather than old parent seed

### Slice E: Conflict handling

Bounded:

- merge conflict persists durable blocked state
- dependents remain blocked
- conflict prompt context includes required merge metadata

Real runtime:

- real conflicted incremental merge blocks the lane and routes to parent AI conflict handling

### Slice F: Full orchestration flow

Bounded:

- all state transitions line up across durable state discovery, lane, blocker, and lifecycle layers

Real runtime:

- child A completes
- daemon merges A upward
- child B unblocks and starts from updated parent state
- final parent reconcile still succeeds after all child merges

## Smallest Safe First Phase

The smallest safe implementation phase is narrower than the whole feature.

Recommended first phase:

1. add durable incremental-merge state
2. record completed-unmerged child state when child run completes
3. process one completed child into parent state
4. expose resulting parent merge audit and lane state
5. do not yet auto-refresh or auto-start dependents

Why this first:

- it proves the daemon can own incremental child-to-parent merge safely
- it avoids mixing readiness-policy changes and child refresh semantics too early
- it gives a real substrate for later blocker and bootstrap logic

## Minimum Real E2E To Claim Flow Progress

Before claiming meaningful flow progress beyond bounded proof, one real E2E should prove:

1. child A completes
2. daemon incrementally merges A into parent
3. child B remains blocked until that merge succeeds
4. child B starts only after merge success
5. child B actually sees parent state that includes A's change

Without that E2E, the feature is only partially implemented, not flow-complete.

## Internal Event And Command Vocabulary

This feature will be easier to implement and test if the daemon uses explicit internal event and command names instead of implicit "something changed, rescan everything" behavior.

The names below are proposed runtime vocabulary for the future implementation.

### Event vocabulary

These are durable or at least well-defined daemon events that should exist conceptually even if the final storage mechanism differs.

#### Child completion events

- `child.run.completed`
- `child.final_commit.recorded`

Meaning:

- a child reached successful terminal completion
- the child now has a mergeable final artifact set, including final commit if required

#### Parent merge-lane events

- `parent.incremental_merge.discovered`
- `parent.incremental_merge.started`
- `parent.incremental_merge.succeeded`
- `parent.incremental_merge.conflicted`
- `parent.incremental_merge.resumed`
- `parent.incremental_merge.already_applied`

Meaning:

- the parent lane discovered completed-unmerged child work during its scan
- the daemon started processing one child merge
- that merge succeeded
- that merge conflicted
- the lane resumed after conflict resolution
- the child had already been durably merged upward, so no duplicate mutation occurred

#### Dependency/unblock events

- `dependency.blocked_on_incremental_merge`
- `dependency.blocked_on_parent_refresh`
- `dependency.unblocked_after_incremental_merge`
- `dependency.unblocked_after_parent_refresh`

Meaning:

- the daemon changed the child blocked reason because the prerequisite is complete but not yet merged, or because bootstrap is stale
- the daemon later cleared that reason after merge or refresh

#### Child refresh events

- `child.parent_refresh.required`
- `child.parent_refresh.started`
- `child.parent_refresh.completed`
- `child.parent_refresh.invalidated`

Meaning:

- the child cannot be admitted against its old parent state
- the daemon is refreshing its parent-derived git/bootstrap state
- refresh succeeded
- a later parent change invalidated the earlier refresh

#### Final parent progression events

- `parent.ready_for_final_reconcile`
- `parent.final_reconcile.started`

Meaning:

- all required children are complete and incrementally merged upward
- the parent can now move into its later AI-owned reconcile/quality/finalize path

### Internal command vocabulary

These should be the main daemon-internal commands or functions used to drive the lane.

#### Scan / worker commands

- `process_pending_incremental_parent_merges()`
- `process_parent_incremental_merge(parent_node_version_id)`
- `select_next_completed_unmerged_child(parent_node_version_id)`

Purpose:

- run the background merge scan and serialize per-parent work

#### Merge execution commands

- `execute_incremental_child_merge(parent_node_version_id, child_node_version_id)`
- `record_incremental_merge_success(...)`
- `record_incremental_merge_conflict(...)`

Purpose:

- perform and persist one child-to-parent merge step

#### Child refresh commands

- `mark_dependent_children_refresh_required(parent_node_version_id, merged_child_node_version_id)`
- `refresh_child_from_parent_state(child_node_version_id)`
- `clear_child_refresh_blocker(child_node_version_id)`

Purpose:

- ensure dependent children do not start from stale parent ancestry

#### Dependency recomputation commands

- `recompute_child_dependency_blockers(child_node_version_id)`
- `recompute_parent_dependent_blockers(parent_node_version_id)`
- `mark_child_ready_if_merge_requirements_satisfied(child_node_version_id)`

Purpose:

- keep admission truth aligned with merge-backed dependency semantics

#### Conflict recovery commands

- `pause_parent_incremental_merge_lane(parent_node_version_id, conflict_id)`
- `resume_parent_incremental_merge_lane(parent_node_version_id)`

Purpose:

- make conflict handling explicit and restart-safe

### Why no separate queue/claim model is preferred here

The repo already leans on:

- background scans over durable authoritative state
- daemon-owned mutation serialization through PostgreSQL advisory locks
- current-state truth in lifecycle/run/blocker/merge records

So this feature should prefer:

- durable per-child incremental-merge state
- durable per-parent merge-lane state
- per-parent advisory locking
- repeated background scans that are safe because merge status is durably inspectable

Only introduce a separate queue/claim model later if the simpler scan-and-lock approach proves insufficient in code.

### Why explicit vocabulary matters

Without explicit names:

- tests will assert vague side effects instead of stable contracts
- logs and workflow events will be inconsistent
- daemon restart behavior will be harder to reason about
- operator surfaces will be less explainable

With explicit names:

- the background runtime can be tested phase by phase
- merge-lane state changes become inspectable
- conflict handling and replay behavior become easier to document and prove

## Tests Required For Event/Command Vocabulary

- child completion makes one completed child discoverable for parent incremental merge
- duplicate scans or replay emit `already_applied` rather than a second merge mutation
- merge success emits started/succeeded in the expected order
- conflict path emits started/conflicted and leaves the lane paused or conflicted
- dependency blocker transitions emit unblock events only after merge success
- refresh-required and refresh-completed child events align with actual admission truth

## Doctrinal Rewrite Map

If this future plan becomes real implementation work, several current repository notes will need explicit doctrinal updates.

The point of this map is to avoid treating the implementation as "just code changes" when the current written model still assumes a different orchestration shape.

### Runtime command loop doctrine

Files:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/pseudocode/modules/wait_for_child_completion.md`
- `notes/pseudocode/modules/collect_child_results.md`

Rewrite needed:

- change the parent flow from "wait for all children, then reconcile parent" to "incrementally merge each completed child upward, then run final parent reconcile after all required child merges are applied"

### Lifecycle doctrine

Files:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/pseudocode/state_machines/node_lifecycle.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

Rewrite needed:

- add or explicitly reject new parent lifecycle states
- define whether merge-lane coordination belongs in lifecycle or run-state/cursor state
- define child blocked-state semantics around incremental merge and parent refresh

### Git / rectification doctrine

Files:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`

Rewrite needed:

- distinguish incremental child-to-parent merges during live orchestration from later full parent rebuild/reconcile
- clarify how incremental merge ordering and final reconcile ordering relate without double-merging

### Database doctrine

Files:

- `notes/specs/database/database_schema_spec_v2.md`

Rewrite needed:

- define the durable coordination records for incremental merge lane state, per-child merge state, and dependent-child refresh truth

### Parent/child contract doctrine

Files:

- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`

Rewrite needed:

- define that successful child completion should advance parent state incrementally
- define how merge conflict pauses or failure decisions interact with the parent incremental merge lane

### Prompt doctrine

Files:

- `notes/specs/prompts/prompt_library_plan.md`

Rewrite needed:

- define child startup context after merged prerequisites
- define parent conflict-resolution prompt context for incremental merge conflict
- redefine final parent reconcile prompt to assume child merges are already applied

### YAML/code-boundary doctrine

Files:

- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`

Rewrite needed:

- clarify whether existing `auto_merge_to_parent` is sufficient or a narrower declarative policy is needed
- keep merge legality, dependency truth, and recovery logic firmly code-owned

### E2E and proving doctrine

Files:

- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

Rewrite needed:

- define the canonical bounded and real-E2E commands for merge-backed sibling dependency flows
- define what completion claims are allowed before real git-backed dependency-visibility E2E exists

## Likely Runtime Hook Points

These are the most plausible code insertion points from the current implementation.

### 1. Child completion detection

- `src/aicoding/daemon/run_orchestration.py`

This is where child runs become `COMPLETE`. A completion-side event or callback needs to make the completed-unmerged child durably discoverable by the parent incremental-merge scan.

### 2. Parent incremental merge worker

- `src/aicoding/daemon/session_records.py`
- possibly a new daemon module, likely something like `src/aicoding/daemon/incremental_parent_merge.py`

Reason:

- the existing background child auto-start loop already lives in daemon session/runtime plumbing
- the new behavior is another background orchestration loop, not a CLI-only mutation

### 3. Dependency blocker reevaluation

- `src/aicoding/daemon/admission.py`

This is where current dependency satisfaction is reduced to lifecycle-state equality. That contract will need expansion.

### 4. Merge execution and audit

- `src/aicoding/daemon/live_git.py`
- `src/aicoding/daemon/child_reconcile.py`

### 5. Operator and AI inspection

- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/operator_views.py`
- `src/aicoding/cli/handlers.py`

## Affected Systems

### Database

- store incremental-merge audit and parent-head lineage strongly enough to make restart/recovery safe
- track whether a dependency edge is satisfied only after merge-backed parent visibility
- track whether a completed child has already been merged upward for the current authoritative parent state
- track whether a blocked child bootstrap is stale relative to the current parent head

### CLI

- expose whether a blocked child is waiting on sibling completion or waiting on sibling merge-to-parent
- expose incremental merge events and current parent merge-backed head used for dependency unblocking

### Daemon

- own the incremental merge trigger, idempotency, conflict handling, and dependent-child rebootstrap logic
- prevent races where two sibling completions try to mutate the same parent merge state concurrently
- own a dedicated parent-monitor loop instead of burying this behavior inside ordinary child admission

### YAML

- clarify whether `auto_merge_to_parent` now means "merge every completed child upward during execution" or whether a narrower explicit policy is needed
- preserve the code/YAML boundary: YAML may request policy, but code remains the authority for legality, ordering, and recovery

### Prompts

- if incremental merge can pause or conflict, add prompt/runtime guidance for the parent or operator so the reason is inspectable
- dependent-child startup context should include which sibling merges are already incorporated into parent state

## Main Risks

- double-merging the same child into the parent during retries or recovery
- invalidating already-bootstrapped dependent children when the parent head changes underneath them
- introducing merge ordering drift between incremental merges and the later full reconcile sequence
- treating content visibility as solved for summaries/docs while git ancestry is still stale, or vice versa
- letting child completion unblock dependency status before the parent loop has durably recorded the corresponding incremental merge

## Verification To Require When This Becomes Real Work

Bounded proof:

- unit and integration coverage for blocker transitions from `blocked_on_dependency` to `blocked_on_incremental_merge` to `ready`
- integration coverage for parent-head mutation and dependent-child rebootstrap/reset logic
- document/note updates for the new policy and invariant surfaces
- bounded tests for the new parent-monitor loop itself, including restart-safe idempotent reprocessing

Real E2E proof:

- a real git-backed sibling chain where child `B` reads or modifies output created by child `A`
- proof that `B` fails without the incremental merge and succeeds with it
- recovery coverage showing the daemon can restart between `A` completion and `B` admission without losing the required parent state

## Suggested First Implementation Slice

Start with the narrowest real contract:

1. only support not-yet-started dependent siblings
2. require a recorded child final commit
3. trigger parent incremental merge immediately when any child completes
4. admit the dependent sibling only after that merge succeeds
5. expose the new blocker/merge state through existing dependency and child-result inspection surfaces

That slice avoids solving mid-run dependent-child rebases before the runtime has a correct durable parent-state contract.
