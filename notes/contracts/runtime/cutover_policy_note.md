# Cutover Policy Note

## Purpose

This document defines when a new node version or rebuilt lineage becomes authoritative after regeneration and rectification.

The broader design already assumes:

- node versions are immutable once created
- regeneration creates superseding node versions
- upstream rectification rebuilds ancestors from seed
- the old lineage should not be discarded too early

What remained underspecified was the exact cutover rule:

- when the new version becomes the authoritative current version
- what happens to active runs on the old version
- whether cutover happens at the changed node, at the subtree, or only after upstream rebuild completes
- what rollback means if rebuild fails

This note makes those decisions explicit enough to guide runtime and DB behavior.

Related documents:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Cutover should be conservative.

Recommended default:

- the new lineage becomes authoritative only after the required rebuilt path is stable

In practice that means:

- do not mark the old lineage fully superseded immediately when a new version is created
- do not assume child-local success is enough if parent outputs still depend on upstream rebuild
- do not destroy old-run traceability during rebuild

The system should favor temporary coexistence of:

- old authoritative lineage
- new in-progress candidate lineage

until the new lineage is proven stable enough to take over.

---

## What “Authoritative” Means

A node version is authoritative when it is the version the system should treat as the active current truth for:

- dependency evaluation
- downstream parent child-final selection
- operator “current node” views
- future regeneration starting points
- merge-to-parent or merge-to-base decisions

Historical versions remain durable and queryable, but they are no longer the current effective version.

---

## Cutover Scopes

The system should distinguish three levels of cutover scope.

## Scope 1: Local node cutover

The changed node version itself is ready to replace its prior version.

## Scope 2: Subtree cutover

The changed node and required regenerated descendants are stable together.

## Scope 3: Upstream lineage cutover

The changed node, its required subtree, and all required rebuilt ancestors up to the chosen stopping point are stable.

Recommended default authoritative scope:

- upstream lineage cutover

Reason:

- parent outputs are reconstructed from child finals
- if upstream has not been rebuilt, the tree’s effective output is not yet stable

---

## Required Cutover Scope Enumeration

`upstream lineage cutover` is only implementation-ready if the runtime can enumerate the exact required scope.

The runtime should expose a conceptual function:

`enumerate_required_cutover_scope(candidate_root_version_id) -> scope_summary`

The returned scope summary must include:

- `candidate_root_version_id`
- required descendant candidate versions
- required ancestor candidate versions
- scope kind such as `local`, `subtree`, or `upstream`
- stopping reason such as `root_reached`, `explicit_scope_boundary`, or `no_parent`
- authoritative baseline version ids the candidate was built against

Enumeration order rule:

- the required candidate version list should be emitted in deterministic replay-safe order
- descendants should appear before rebuilt ancestors
- where multiple candidates remain unordered after dependency analysis, use a stable layout or creation-order tie break

Current implementation status:

- `src/aicoding/daemon/rebuild_coordination.py` exposes `enumerate_required_cutover_scope(...)`
- rebuild-backed candidates now enumerate required sibling and ancestor membership from durable `RebuildEvent` history
- emitted candidate ordering is deterministic and descendant-first so replay-sensitive scope members appear before rebuilt ancestors
- non-rebuild candidates still collapse to `local` scope
- cutover-readiness inspection now aggregates blockers across the enumerated required scope instead of judging only the requested candidate version
- manual cutover now uses that same grouped scope for authority transfer, rebinding each switched logical node's live runtime ownership to the new authoritative version inside the same mutation batch
- when the requested candidate is a rebuilt ancestor, cutover-readiness may return `ready_with_follow_on_replay` if the only remaining blockers belong to dependency-invalidated fresh-restart descendants that are explicitly waiting for post-cutover parent refresh/rematerialization
- direct cutover of the dependency-invalidated descendant itself remains blocked; the follow-on exception is grouped-scope-only

Recommended default rule:

- unless a narrower explicit policy is provided and proven safe, stop only when the rebuilt path reaches the highest ancestor whose effective output still consumes the candidate subtree

Implementation rule:

- cutover readiness must be computed against this enumerated scope, not against the candidate root in isolation
- manual candidate cutover should switch authority for the full enumerated scope, not only for the requested root candidate version

Current limitation:

- grouped readiness and manual cutover now share the same required scope, but the broader post-cutover fresh-rematerialization narrative still remains partial and is not yet proved end to end for every rebuild-backed lineage shape with real prerequisite merge progression

---

## Default Cutover Policy

The default policy should be:

1. create superseding node version
2. compile new workflow
3. regenerate required descendants
4. rebuild changed node from seed
5. rebuild required ancestors from seed
6. if all required rebuilt nodes succeed, mark new lineage authoritative
7. only then mark replaced lineage as superseded

This means the old lineage remains authoritative during candidate rebuild.

---

## Why Early Cutover Is Dangerous

Early cutover creates risks such as:

- dependency calculations pointing at incomplete new nodes
- parent merge logic consuming partially rebuilt child outputs
- operators seeing “current” versions that are not yet stable
- regeneration chains using incomplete candidate lineage as the new baseline

The system should avoid these hazards unless a narrower cutover policy is explicitly configured.

---

## Old-Version Run Handling

One of the key cutover questions is what to do with active runs on older versions.

Recommended default behavior:

## Case 1: Old version has no active run

Action:

- leave it as authoritative until new lineage is stable
- then mark it superseded

## Case 2: Old version has an active run and new rebuild is requested

Action:

- do not silently destroy the active old run
- choose one of:
  - let old run continue if policy allows
  - cancel old run explicitly before new candidate proceeds
  - pause old run and require operator decision

Recommended default:

- pause or cancel explicitly before allowing conflicting active rebuild execution

Implementation staging note:

- the current implementation takes the stricter simpler path for now: creating a superseding candidate version is rejected while the logical node has an active or paused run
- explicit pause/cancel-then-supersede flows remain the supported path until later runtime orchestration phases add more nuanced in-daemon conflict resolution

Reason:

- two active lineages for the same logical node can easily create ambiguity

## Case 3: Old active run finishes while new lineage is rebuilding

Action:

- old run completion remains historical truth for the old lineage
- it does not block candidate lineage completion
- final authoritative cutover still depends on the candidate lineage policy

## Case 4: New lineage fails before cutover

Action:

- old lineage remains authoritative
- old run history remains intact
- new candidate lineage remains historical failed attempt unless later retried

---

## Active-Run Conflict Policy

The system should not allow ambiguous simultaneous active primary execution for multiple versions of the same logical node without explicit policy.

Recommended default:

- one active authoritative run path per logical node

That means:

- if an old version is actively running and a new superseding rebuild is requested, the runtime must explicitly resolve the conflict

Resolution options:

1. cancel old run
2. pause old run
3. defer new rebuild

Recommended default:

- pause old run, record why, then proceed with new rebuild only after the conflict is explicit

If implementation wants a stricter simpler first version:

- cancel old run before superseding rebuild begins

---

## Candidate Lineage State

During rebuild, the new lineage should be treated as a candidate lineage.

Candidate lineage properties:

- fully durable
- queryable
- not yet authoritative
- eligible for its own run/session history
- should not replace old lineage in “current effective” views until cutover occurs

This suggests the implementation may need to distinguish:

Implementation staging note:

- the current implementation now blocks candidate-version cutover when unresolved durable merge conflicts exist for that candidate version
- candidate cutover readiness is now also exposed explicitly through a dedicated read surface that reports:
  - unresolved merge conflicts
  - missing stable subtree/upstream rebuild completion for rebuild-backed candidates
  - active or paused authoritative runs
  - active primary sessions still attached to the authoritative run
- blocked cutover attempts now leave durable `rebuild_events` audit instead of only returning a conflict
- the runtime now supports the direct live git merge/finalize path for parent finalize flow
- rebuild-driven working-tree reset and rectification mechanics are still deferred to the later rebuild-specific git slices

- latest created version
- latest authoritative version

If those are not always the same during rebuild, views and CLI should reflect that.

---

## Suggested Authoritative-State Model

The design should support a conceptual distinction between:

- `latest_version`
- `authoritative_version`

There are multiple ways to model this.

### Option A: Derived authoritative version by supersession and cutover rules

Pros:

- fewer columns

Cons:

- harder queries
- harder to represent candidate-versus-authoritative cleanly

### Option B: Explicit authority marker

Possible forms:

- dedicated current-version table
- authority flag on node version
- lineage-status state

Recommended direction:

- use an explicit authoritative-version mechanism during implementation-grade DB refinement

Canonical DB direction:

- use an explicit current-version selector that stores:
  - authoritative version
  - latest created version
- keep candidate lineage queryable separately from authoritative lineage

This note does not force the final exact table names, but the runtime concept should now be treated as required rather than optional.

---

## Authoritative-Baseline Drift

If a candidate rebuild starts from authoritative baseline A and the authoritative lineage advances to baseline B before cutover:

- the candidate must not auto-cut over
- cutover readiness must report a blocker equivalent to `authoritative_lineage_changed_since_rebuild_started`
- the candidate may later be rebuilt or revalidated from B according to policy

Reason:

- otherwise the system can cut over a candidate lineage built against stale assumptions after the active authoritative tree already changed

---

## Canonical Live Coordination Blockers

Cutover-readiness and rebuild-coordination surfaces should expose explicit blocker kinds such as:

- `active_authoritative_run`
- `active_authoritative_primary_session`
- `candidate_compile_failed`
- `candidate_merge_conflict`
- `candidate_replay_incomplete`
- `required_descendant_not_stable`
- `required_ancestor_not_stable`
- `approval_required`
- `candidate_superseded`
- `authoritative_lineage_changed_since_rebuild_started`

These blocker kinds should be durable and inspectable rather than reconstructed ad hoc from mixed tables at read time.

---

## Cutover Preconditions

Before new lineage becomes authoritative, at minimum verify:

- the changed node completed successfully
- all required regenerated descendants completed successfully
- all required ancestor rectifications completed successfully
- quality gates succeeded for each required rebuilt node
- final commits are recorded for required rebuilt nodes
- no unresolved merge conflicts remain
- no blocking user gate remains unresolved
- the candidate baseline still matches the current authoritative lineage or has been explicitly revalidated after baseline drift

If any precondition fails:

- cutover must not occur

The candidate lineage should be considered `stable_for_cutover` only if all required scope members:

- exist
- are still the current candidate versions for their logical nodes
- compiled successfully
- have required final commits or replay-complete state recorded
- have no unresolved candidate merge conflicts
- have no unresolved user or policy gate
- have not been invalidated by supersession or authoritative-baseline drift

---

## Failure Before Cutover

If the candidate lineage fails before cutover:

1. leave old lineage authoritative
2. record the failure in candidate lineage history
3. do not partially supersede the old lineage
4. allow later retry or regeneration from the old authoritative baseline or from the failed candidate according to policy

Recommended default:

- preserve old authoritative lineage and treat candidate failure as non-authoritative history

---

## Partial Upstream Success

If some ancestors rebuild successfully but the full required path does not:

Recommended default:

- no authoritative cutover

Reason:

- partial upstream success still means the top effective output may be inconsistent

Possible future advanced policy:

- bounded-scope cutover if rebuild stopping point is intentionally below the top node

But this should not be the default.

---

## User-Gated Cutover

Cutover may be user-gated.

This is especially important for:

- merge to parent
- merge to base
- major rectification results

Behavior:

1. candidate lineage reaches stable pre-cutover state
2. a summary is registered
3. node transitions to `PAUSED_FOR_USER`
4. explicit user approval triggers cutover/merge continuation

This keeps authority transfer inspectable and reversible until approval.

---

## Candidate Replay Versus Live Incremental Merge

The runtime now has two distinct merge models.

### Authoritative live incremental merge

- daemon-owned
- completion-driven
- mutates the current authoritative parent lineage in place
- records actual applied merge order as historical runtime truth

### Candidate-lineage replay

- rebuild-owned
- deterministic and dependency-safe
- replays child finals into a fresh candidate lineage from seed or baseline state
- prepares a candidate lineage for later cutover

Implementation rule:

- candidate cutover must evaluate candidate replay state, not live incremental merge state
- authoritative live `applied_merge_order` is useful audit history but is not the binding replay order for candidate rebuild unless the candidate child set is identical and no dependency-visible inputs changed

---

## Candidate Replay Input Selection

Candidate replay should source child inputs in this precedence order:

1. regenerated candidate child final for that lineage
2. explicitly reused authoritative child final whose reuse classification is still valid
3. otherwise the child is not replayable yet and candidate replay remains incomplete

Recommended replay order:

- topological over the rebuilt and reused child set
- if multiple children remain unordered after dependency analysis, use a stable layout or ordinal order

Reason:

- authoritative live merge order is completion-driven operational history
- candidate replay should be deterministic so rebuild audit and cutover-readiness stay reproducible

---

## Rollback Semantics

In this model, rollback should usually mean:

- do not cut over
- keep old lineage authoritative

Because the system is versioned, rollback is not usually:

- mutating the old version back into place

Instead, rollback is primarily:

- refusing authority transfer to the failed or rejected candidate

This is simpler and more auditable than trying to “undo” the old lineage.

---

## Reuse And Invalidation Rules During Candidate Rebuild

A sibling child may be reused into a candidate lineage only if all of the following remain true:

- its authoritative final exists
- it is not itself being regenerated in the candidate lineage
- it does not depend directly or transitively on rebuilt sibling output that changes effective parent-visible state
- its compile/render inputs remain equivalent for the candidate lineage
- policy does not require rematerialization against a new candidate parent baseline

A sibling must be regenerated or blocked pending refresh if any of the following are true:

- it depends on rebuilt sibling output that changes effective parent-visible state
- it was bootstrapped from parent state that is no longer the candidate parent baseline it would run against
- its compile/render inputs changed in the candidate lineage
- its descendants or generated structure depend on rebuilt sibling or parent output

Recommended implementation surface:

- persist a child replay classification such as `reuse`, `regenerate`, or `blocked_pending_parent_refresh`
- persist an explanatory reason such as `reused_unaffected_child`, `invalidated_by_dependency_change`, `invalidated_by_parent_state_change`, or `invalidated_by_compile_input_change`

---

## Pseudocode

```python
def maybe_cut_over_lineage(logical_node_id, candidate_root_version_id):
    candidate_scope = enumerate_required_cutover_scope(candidate_root_version_id)
    if not scope_is_stable(candidate_scope):
        return "not_ready"

    if candidate_replay_is_incomplete(candidate_scope):
        return "not_ready"

    if authoritative_baseline_changed(candidate_scope):
        return "not_ready"

    if has_unresolved_user_gate(candidate_scope):
        pause_for_user(candidate_root_version_id, reason="cutover_approval_required")
        return "paused_for_user"

    mark_candidate_scope_authoritative(candidate_scope)
    mark_replaced_scope_superseded(candidate_scope)
    return "cutover_complete"
```

This is intentionally simple. The implementation must expand:

- what the required scope is
- how authority markers are updated
- how views switch over
- how replay completeness is computed
- how reused versus regenerated child finals are selected
- how authoritative-baseline drift blocks a pending cutover

---

## DB Implications

The current DB model supports supersession lineage, but implementation may need a clearer authority concept.

Likely options:

### Option 1: Dedicated authoritative-version view or table

Purpose:

- resolve current effective version cleanly during candidate rebuild

### Option 2: Additional lineage status field

Possible conceptual values:

- `candidate`
- `authoritative`
- `superseded`
- `failed_candidate`

This could live as:

- a new node version status layer
- a dedicated lineage table

Recommended direction:

- add explicit authority modeling during migration-grade DB refinement if concurrent old/new lineage states are expected in practice

---

## CLI Implications

The CLI should allow users and operators to distinguish:

- latest version created
- currently authoritative version
- candidate versions awaiting cutover

Likely useful commands:

- `ai-tool node lineage --node <id>`
- `ai-tool node show --node <id> --authoritative`
- `ai-tool rebuild show --node <id>`
- `ai-tool merge approve --node <id>`

Potential useful addition:

- `ai-tool node authoritative --logical-node <id>`

If naming differs, the capability should still exist.

---

## Interaction With Parent Failure Logic

If a child candidate lineage fails before cutover:

- the parent should still reference the old authoritative child lineage
- parent decision logic should treat the failed candidate as diagnostic history, not as current effective child state

This prevents accidental upstream contamination from failed candidate rebuilds.

---

## Interaction With Dependency Evaluation

Until cutover occurs:

- dependency evaluation should use authoritative lineage
- not merely the newest created candidate version

This is another reason authority must be explicit conceptually.

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/git/git_rectification_spec_v2.md`
2. `notes/specs/runtime/node_lifecycle_spec_v2.md`
3. `notes/specs/database/database_schema_spec_v2.md`
4. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the cutover and old-run gaps.

---

## Exit Criteria

This note is complete enough when:

- cutover scope is explicit
- authoritative versus candidate lineage is explicit
- old active-run handling is explicit
- rollback semantics are explicit
- DB and CLI implications are identified

At that point, supersession cutover is concrete enough to stop being a dangerous implied behavior.
Implementation note: candidate cutover now has an additional rebuild-specific gate. If a candidate version has recorded subtree/upstream rebuild events, at least one `stable` rebuild event must exist before cutover is allowed. Cutover-only audit events do not themselves create a false rebuild-stability requirement.
