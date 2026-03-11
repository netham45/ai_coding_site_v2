# Phase E2E-00: E2E Feature Generation Strategy

## Goal

Define how real end-to-end tests will be generated so every existing feature is exercisable through real code rather than only through simulation, bounded integration, or internal helper proof.

## Rationale

- Rationale: The repository now has feature plans, flow plans, bounded flow tests, and the first real E2E checkpoints, but it still needs a deterministic way to derive full real-code E2E coverage for every implemented feature.
- Reason for existence: This phase exists to prevent ad hoc E2E authoring and to ensure every existing feature receives a real-code test target instead of being skipped because it is harder to exercise than the convenient fast route.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: E2E work extends the testing model rather than replacing it.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: every user-visible action must eventually be scriptable and therefore E2E-exercisable.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: E2E tests must prove reconstructible history rather than only runtime success.
- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`: this E2E track is one branch of the broader doctrine-hardening plan.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: every E2E plan must include durable-state assertions when the feature mutates or depends on persisted state.
- CLI: every CLI-facing feature must be exercised through the real CLI subprocess path in its strongest E2E proof.
- Daemon: every daemon-owned mutation or inspection feature must be exercised through the real daemon process and real API boundary where applicable.
- Website: every website-facing feature must be exercised through the real browser and website route in its strongest E2E proof where applicable.
- YAML: every YAML-defined behavior claimed as product behavior must be exercised through actual load/compile/runtime effects instead of only schema or file-presence proof.
- Prompts: prompt-linked behavior must be exercised through actual prompt selection, delivery, and/or prompt-history effects where applicable.
- Notes: update E2E notes and coverage checklists so they reflect real-code proof status rather than bounded flow assumptions.
- Tests: create reusable E2E suite families so features are proven in coherent product narratives instead of one isolated assertion per feature.
- Performance: keep E2E scopes bounded enough to be runnable, but do not weaken them by replacing real boundaries with shortcuts.

## Generation Method

Generate E2E tests for existing features using this method:

1. Start from the existing feature plan.
2. Identify the feature's affected systems: database, CLI, daemon, website, YAML, prompts.
3. Identify the strongest user-visible or operator-visible trigger for the feature.
4. Identify the real-code path that should exercise that trigger:
   - CLI subprocess
   - daemon HTTP API through a real daemon subprocess
   - website UI through a real browser and website process where the feature has a browser surface
   - real PostgreSQL state
   - real filesystem workspace
   - real git repo if git is part of the feature
   - real tmux/provider integration if session/provider behavior is part of the feature
5. Identify the minimum durable assertions required after execution:
   - resulting runtime state
   - audit/history/provenance rows or views
   - inspectability through CLI/API
   - recovery-relevant state where applicable
6. Group the feature into the smallest reusable E2E suite family that matches its runtime dependencies.
7. Record the feature-to-suite mapping in `06_e2e_feature_matrix.md`.
8. Only mark the feature E2E-covered when the real-code suite exists and its canonical command is documented.

## E2E Generation Rules

- Do not generate one trivial E2E file per feature if multiple features belong to the same real product narrative.
- Do not collapse distinct high-risk boundaries into one vague mega-test with weak assertions.
- Prefer reusable suite families organized around runtime capability:
  - core orchestration
  - compile and YAML/runtime policy behavior
  - session and recovery behavior
  - child scheduling and reconciliation
  - quality, docs, provenance, and audit
  - git, rebuild, and cutover
- Every feature must still have an explicit row in the feature matrix, even when multiple features share one suite family.
- A feature is not E2E-covered if the suite that mentions it still uses fake session backends, in-process bridge clients as the only proof, direct DB mutations to skip runtime work, or synthetic outputs to bypass the core behavior being claimed.

## Deliverables

- an explicit E2E generation contract
- a wave plan for each major E2E suite family
- a feature-to-suite matrix covering every existing feature plan
- canonical commands for running each E2E suite family

## Exit Criteria

- every existing feature plan is mapped to at least one real-code E2E suite target
- every mapped suite states the real runtime boundaries it must exercise
- the repository has a repeatable method for generating new E2E plans for future features
