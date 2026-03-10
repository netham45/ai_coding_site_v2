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

## Cutover Preconditions

Before new lineage becomes authoritative, at minimum verify:

- the changed node completed successfully
- all required regenerated descendants completed successfully
- all required ancestor rectifications completed successfully
- quality gates succeeded for each required rebuilt node
- final commits are recorded for required rebuilt nodes
- no unresolved merge conflicts remain
- no blocking user gate remains unresolved

If any precondition fails:

- cutover must not occur

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

## Pseudocode

```python
def maybe_cut_over_lineage(logical_node_id, candidate_root_version_id):
    candidate_scope = get_required_cutover_scope(candidate_root_version_id)
    if not scope_is_stable(candidate_scope):
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
