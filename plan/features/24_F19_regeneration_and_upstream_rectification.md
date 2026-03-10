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
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 determines how rebuilt children are merged back into the parent.
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
