# Phase F19: Regeneration And Upstream Rectification

## Goal

Support subtree regeneration and ancestor rebuild without premature cutover.

## Rationale

- Rationale: A long-lived orchestration tree needs a principled way to rebuild stale or invalid sections without corrupting the current accepted lineage.
- Reason for existence: This phase exists to make regeneration and upstream rectification controlled operations rather than destructive rewrites.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 provides the supersession mechanism regeneration uses.
- `plan/features/12_F17_deterministic_branch_model.md`: F17 defines branch lineage across rebuilt candidates.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 now distinguishes authoritative live incremental merge from candidate-lineage replay; F19 uses the replay side of that split.
- `plan/features/22_F20_conflict_detection_and_resolution.md`: F20 handles non-trivial conflicts during rebuild and cutover.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`

## Scope

- Database: rebuild events, candidate lineage, rectification progress.
- CLI: regenerate, rectify-upstream, and rebuild-history commands.
- Daemon: candidate lineage creation, subtree regeneration, and rectification.
- YAML: rectification tasks and rebuild policies.
- Prompts: regenerated execution and parent rectify prompts.
- Tests: exhaustive candidate-lineage safety, sibling reuse, rectification failure, and no-premature-cutover coverage.
- Performance: benchmark rebuild and rectification over multi-node trees.
- Notes: update rectification/cutover notes if implementation tightens scope rules.

## Implementation Clarifications

- Candidate replay is a different runtime path from authoritative live incremental merge.
- Regeneration should rebuild a candidate lineage from seed or baseline state rather than mutating the current authoritative parent lane in place.
- Candidate replay should prefer regenerated candidate child finals, then explicitly reused authoritative child finals, and should treat missing finals as replay blockers.
- Candidate replay ordering should be deterministic and dependency-safe for the rebuilt child set; authoritative live `applied_merge_order` remains audit history, not the binding replay order.
- Sibling reuse versus regeneration must be classified from dependency visibility and effective parent-state change, not only subtree membership.
- Candidate lineage stability for cutover requires compile success, replay success where applicable, conflict-free state, satisfied gates, and stable required scope members.

## Required Runtime Decisions Before Implementation

- Define `enumerate_required_cutover_scope(...)` for candidate lineages, including ancestor and descendant membership plus stopping reason.
- Define `classify_candidate_child_reuse(...)` so reuse, regeneration, and parent-refresh blocking are explicit and inspectable.
- Define how authoritative-baseline drift blocks cutover when the authoritative lineage changes during candidate rebuild.
- Bind the phase to the existing CLI proving surfaces instead of inventing a replacement command family.
