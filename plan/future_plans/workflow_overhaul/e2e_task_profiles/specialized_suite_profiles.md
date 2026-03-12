# Specialized E2E Suite Profiles

These profiles cover suite families that are broader than one canonical flow and deserve dedicated task identities.

They still inherit from the base `task.e2e` contract, but their proving surface spans a larger runtime boundary or a grouped feature family.

## `task.e2e.compile_variants_and_diagnostics`

- Primary suite target: `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`
- Goal: Prove compile variants, invalid-YAML failures, override resolution, hook expansion, rendering freeze, and compile diagnostics.
- Use when:
  - compile-stage behavior changes
  - YAML/policy/prompt compile surfaces change

## `task.e2e.dependency_and_child_materialization`

- Primary suite target: `tests/e2e/test_e2e_dependency_and_child_materialization_real.py`
- Goal: Prove dependency-blocked admission, child materialization, richer blocker explanation, and readiness transitions.
- Use when:
  - dependency semantics change
  - child scheduling or blocker surfaces change

## `task.e2e.child_merge_and_reconciliation`

- Primary suite target: `tests/e2e/test_e2e_child_merge_and_reconciliation_real.py`
- Goal: Prove child result collection, reconciliation, manual-tree interaction, and hybrid authority behavior.
- Use when:
  - child merge or reconcile semantics change
  - manual or hybrid reconciliation behavior changes

## `task.e2e.session_binding_and_resume`

- Primary suite target: `tests/e2e/test_e2e_session_binding_and_resume_real.py`
- Goal: Prove session bind, attach, resume, show-current, and stale-session recovery.
- Use when:
  - session-control or recovery behavior changes

## `task.e2e.tmux_session_runtime`

- Primary suite target: `tests/e2e/test_e2e_tmux_session_runtime_real.py`
- Goal: Prove tmux-backed launch, idle detection, screen polling, nudge behavior, and runtime inspection.
- Use when:
  - tmux backend or idle-classification behavior changes

## `task.e2e.provider_recovery`

- Primary suite target: `tests/e2e/test_e2e_provider_recovery_real.py`
- Goal: Prove provider-aware recovery behavior where provider-specific restart semantics matter.
- Use when:
  - provider-specific recovery behavior changes

## `task.e2e.failure_escalation_and_intervention`

- Primary suite target: `tests/e2e/test_e2e_failure_escalation_and_intervention_real.py`
- Goal: Prove failure taxonomy, escalation, pause gates, intervention actions, and parent decision logic.
- Use when:
  - failure or intervention behavior changes

## `task.e2e.quality_chain`

- Primary suite target: `tests/e2e/test_e2e_quality_chain_real.py`
- Goal: Prove validation, review, testing, provenance, and docs gates as one end-to-end quality narrative.
- Use when:
  - quality-chain ordering or quality-library behavior changes

## `task.e2e.prompt_and_summary_history`

- Primary suite target: `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
- Goal: Prove prompt delivery, summary registration, attempt history, and prompt-pack behavior.
- Use when:
  - prompt history or summary persistence changes

## `task.e2e.provenance_and_docs`

- Primary suite target: `tests/e2e/test_e2e_provenance_and_docs_real.py`
- Goal: Prove provenance extraction, rationale inspection, and generated docs surfaces after live work.
- Use when:
  - provenance extraction or documentation-generation behavior changes

## `task.e2e.audit_and_reproducibility`

- Primary suite target: `tests/e2e/test_e2e_audit_and_reproducibility_real.py`
- Goal: Prove reconstructible runtime history, database-backed audit views, and reproducibility surfaces.
- Use when:
  - audit-history or reproducibility behavior changes

## `task.e2e.branch_identity_and_history`

- Primary suite target: `tests/e2e/test_e2e_branch_identity_and_history_real.py`
- Goal: Prove deterministic branch identity, branch history, and related provenance continuity.
- Use when:
  - branch-model behavior changes

## `task.e2e.merge_conflict_and_resolution`

- Primary suite target: `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`
- Goal: Prove real merge-conflict creation, conflict inspection, pause, and resolution.
- Use when:
  - conflict-detection or conflict-resolution behavior changes

## `task.e2e.live_git_merge_and_finalize`

- Primary suite target: `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
- Goal: Prove live child mergeback, finalize behavior, and resulting audit surfaces in a real repository.
- Use when:
  - live git merge or finalize execution changes

## `task.e2e.regeneration_and_upstream_rectification`

- Primary suite target: `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
- Goal: Prove regenerate, grouped rebuild, upstream rectify, and resulting branch/history state.
- Use when:
  - rectification or rebuild-cutover behavior changes

## `task.e2e.rebuild_cutover_coordination`

- Primary suite target: `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
- Goal: Prove live rebuild blockers, cutover coordination, and cutover-readiness behavior.
- Use when:
  - cutover coordination behavior changes

## `task.e2e.incremental_parent_merge`

- Primary suite target: `tests/e2e/test_e2e_incremental_parent_merge_real.py`
- Goal: Prove incremental parent merge lanes, sibling unblock, stale-child refresh, conflict handoff, and restart-safe merge progression.
- Use when:
  - incremental merge behavior changes

## `task.e2e.full_epic_tree_runtime`

- Primary suite target: `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
- Goal: Prove full hierarchy runtime propagation from task to plan to phase to epic, including mergeback and authoritative lineage movement.
- Use when:
  - cross-tier propagation behavior changes
  - one flow alone is too narrow to prove the feature claim
