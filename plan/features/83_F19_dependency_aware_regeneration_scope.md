# Phase F19: Dependency-Aware Regeneration Scope

## Goal

Ensure regeneration and upstream rectification expand scope to include sibling-dependent nodes that become stale when a prerequisite sibling is reset or regenerated.

## Rationale

- Rationale: The current regeneration model is descendant-only, but sibling dependency semantics mean a regenerated child can invalidate other siblings even when their own prompts or structure did not change directly.
- Reason for existence: This phase exists to prevent rebuilt candidate and cutover lineages from silently mixing regenerated prerequisite children with stale dependent sibling outputs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: persist enough rebuild-event detail to show when regeneration scope expanded because of reverse sibling dependencies and which logical nodes were pulled into the candidate closure.
- CLI: existing rebuild-history, lineage, rebuild-coordination, cutover-readiness, dependency, and child-result inspection surfaces should explain when a sibling was regenerated because it depended on another regenerated sibling and why it could not be reused.
- Daemon: replace descendant-only regeneration scope with a dependency-aware closure that includes reverse sibling dependents and their required descendants before parent rectification proceeds.
- Website: no new browser-owned orchestration is needed, but daemon-backed rebuild and lineage views should eventually surface dependency-driven scope expansion clearly.
- YAML: no new live coordination logic moves into YAML; dependency structure stays declarative while regeneration-scope expansion remains code-owned.
- Prompts: prompt/runtime context should eventually explain dependency-driven regeneration when operators or parent AI inspect why a sibling was superseded unexpectedly.
- Tests: add bounded, integration, and real E2E proof that `A -> B` regeneration supersedes `B` before parent rectification while unrelated siblings remain reusable.
- Performance: reverse-dependency closure calculation must stay cheap enough for subtree regeneration on parents with larger sibling sets and must avoid repeated broad graph rescans where possible.
- Notes: update the regeneration, rectification, and cutover doctrine so “reuse unaffected siblings” explicitly excludes siblings invalidated by dependency on regenerated nodes.

## Proposed Implementation Direction

1. Add a daemon-owned regeneration-scope helper that computes one rebuild closure for:
   - the changed node
   - required descendants
   - any siblings with direct or transitive reverse dependency paths from those regenerated nodes
   - the required descendants of those newly included dependent siblings
2. Use that closure during candidate creation so every logically invalidated sibling receives a superseding candidate version before upstream rectification.
3. Keep truly unaffected siblings reusable by authoritative final commit, but only when they are outside the dependency-expanded closure.
4. Add a defensive parent-rectification guard so candidate reconcile cannot proceed with a stale dependent sibling version if scope expansion somehow failed.
5. Extend rebuild history payloads and operator inspection text so dependency-driven scope expansion is visible and auditable.

## Runtime Clarifications

- The scope helper should align with the candidate-lineage contract in `enumerate_required_cutover_scope(...)`, so dependency-expanded siblings appear in the same required replay and cutover-readiness scope rather than as an implementation-only side list.
- Dependency-aware scope expansion should persist a reuse classification per affected sibling, not only a boolean “included/excluded” result.
- A sibling outside the dependency-expanded closure may remain reusable by authoritative final commit, but a sibling inside the closure must not be replayed from stale authoritative output even if its own prompt text did not change.
- Candidate replay order for the resulting rebuilt child set should be deterministic and dependency-safe; this feature should not import authoritative live completion order into candidate replay.

## Verification Expectations

- Bounded proof:
  - regenerating `A` in `A -> B` supersedes `B`
  - regenerating `A` in `A -> B -> C` supersedes transitive dependent siblings
  - unrelated sibling `D` remains reusable and is not pulled into the rebuild closure
  - candidate parent reconcile refuses or flags mixed lineage if a stale dependent sibling remains attached
- Integration proof:
  - daemon/API lineage, rebuild-history, rebuild-coordination, and cutover-readiness reads show dependency-driven scope expansion and candidate creation for dependent siblings
- Real E2E proof:
  - a real regenerate-and-rectify flow proves the rebuilt parent lineage does not replay regenerated prerequisite work together with stale dependent sibling output and that the cutover scope reports the invalidated sibling as required

## Exit Criteria

- regeneration scope is no longer descendant-only when sibling dependency invalidation applies
- parent rectification cannot silently reuse stale dependent sibling finals
- rebuild-history and lineage inspection can explain why dependent siblings were superseded
- notes and proving layers explicitly cover the dependency-aware reuse rule
