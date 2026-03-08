# Cross-Spec Gap Matrix

## Purpose

This document records the first structured gap and contradiction review across the current design set.

It compares:

- original design goals
- major tracked features
- YAML inventory and built-in library planning
- database schema design
- runtime pseudocode planning
- CLI surface design
- git rectification design

The goal is to identify:

- missing artifacts
- contradictions across specs
- underspecified behaviors
- priority areas for v2 rewrite

Related documents:

- `notes/full_spec_expansion_plan.md`
- `notes/major_feature_inventory.md`
- `notes/spec_traceability_matrix.md`
- `notes/yaml_inventory_v2.md`
- `notes/default_yaml_library_plan.md`
- `notes/database_schema_v2_expansion.md`
- `notes/runtime_pseudocode_plan.md`

---

## Classification Model

Each row should use one primary gap class:

- `missing_artifact`
- `underspecified`
- `cross_spec_mismatch`
- `needs_decision`
- `likely_new_schema`
- `likely_new_db_structure`
- `likely_new_cli_surface`
- `likely_new_pseudocode`

Priority values:

- `critical`
- `high`
- `medium`
- `low`

Status values:

- `open`
- `in_review`
- `resolved_in_principle`
- `appendix_specified`
- `implementation_open`
- `deferred`

---

## Highest-Priority Cross-Spec Gaps

These are the most important remaining gaps after the v2 rewrite and appendix pass.

1. Child materialization and scheduling still needs a dedicated algorithm/spec pass.
2. Hook expansion ordering and composition still needs a dedicated algorithm/spec pass.
3. Pause/failure/workflow event-history persistence is still a real design choice, not just implementation detail.
4. Summary taxonomy and source-role taxonomy still need to be frozen canonically.
5. Branch naming and authoritative-version modeling still need final implementation-facing decisions.
6. Manual-tree and auto-tree coexistence rules are still not specified deeply enough.
7. Old-version active-run handling and invalid dependency-graph handling are still open.

---

## Gap Matrix

| Gap ID | Feature IDs | Area | Gap Class | Priority | Status | Current State | Needed Next |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP-001 | F22, F23, F29 | Review/testing/docs modeling | missing_artifact | critical | resolved_in_principle | V2 YAML/DB/runtime/CLI docs now treat review, testing, and docs as first-class families with likely persistence models. | Fold the model into implementation artifacts and verify no remaining contradictions in later review. |
| GAP-002 | F25 | Parent failure decision logic | likely_new_pseudocode | critical | appendix_specified | The dedicated parent failure decision spec now defines failure classes, outcomes, counters, decision order, pseudocode, and DB/CLI implications. | Fold the decision model into canonical lifecycle/runtime/DB docs and remove stale weaker wording there. |
| GAP-003 | F12, F34 | Session recovery semantics | underspecified | critical | appendix_specified | The session recovery appendix now defines scenario handling, replacement-session rules, provider-agnostic recovery, git mismatch behavior, and pseudocode. | Fold the recovery model into canonical runtime/DB/CLI docs and freeze live authority boundaries. |
| GAP-004 | F21, F22, F23, F29, F30 | Quality-gate ordering | needs_decision | critical | resolved_in_principle | V2 YAML/lifecycle/runtime/git docs freeze the default order: validation, review, testing, provenance, docs, finalize. | Verify this order in implementation planning and note any allowed override boundaries. |
| GAP-005 | F15, F19 | Child materialization and scheduling | likely_new_pseudocode | critical | open | Layout and child ideas exist, but creation idempotency, readiness calculation, and scheduling rules are not fully defined. | Write child creation/scheduling algorithms and verify required DB state. |
| GAP-006 | F03, F06, F26 | Hook expansion algorithm | likely_new_pseudocode | high | open | V2 YAML clarifies hook families, but multi-hook ordering and insertion semantics are still not fully frozen algorithmically. | Write a focused hook compilation appendix with ordering and conflict examples. |
| GAP-007 | F23 | Testing persistence model | likely_new_db_structure | high | resolved_in_principle | V2 DB and review/testing/docs plan now define `test_results` and testing YAML families. | Confirm exact fields/status taxonomy during implementation-grade DB design. |
| GAP-008 | F22 | Review persistence model | likely_new_db_structure | high | resolved_in_principle | V2 DB and review/testing/docs plan now define `review_results` and review YAML families. | Confirm exact findings/result schema during implementation-grade DB design. |
| GAP-009 | F21 | Validation result model | likely_new_db_structure | high | resolved_in_principle | V2 DB now defines `validation_results`, though exact evidence schema may still evolve. | Confirm status/evidence taxonomy in migration-grade detail. |
| GAP-010 | F33 | Isolated environment support | missing_artifact | high | implementation_open | The runtime environment policy note now defines isolation modes, workflow/runtime boundary, failure semantics, and recommends optional bounded support or explicit deferment. | Mark it as intentionally deferred or bounded optional in implementation planning. |
| GAP-011 | F32 | Action automation mapping | missing_artifact | high | resolved_in_principle | The action automation matrix now maps user-visible actions to CLI/runtime/DB/audit surfaces. | Fold missing command semantics into CLI implementation planning. |
| GAP-012 | F09, F24, F25 | Pause and failure event history | likely_new_db_structure | high | resolved_in_principle | The workflow-event note and DB/runtime/CLI fold-ins now freeze a narrow first-implementation `workflow_events` model for pause, recovery, parent-decision, and cutover transitions. | Fold the frozen event contract into implementation-grade runtime, DB read-model, and CLI planning. |
| GAP-013 | F30 | Provenance identity stability | underspecified | high | resolved_in_principle | The provenance identity strategy note now defines layered identity, confidence handling, rename/move treatment, and DB/runtime implications. | Fold the strategy into implementation-grade provenance design. |
| GAP-014 | F05 | Concrete default YAML library | missing_artifact | high | in_review | The default YAML library plan and v2 YAML spec enumerate the built-in file set, but the actual YAML files are still not authored. | Turn planned file inventory into real built-in YAML definitions. |
| GAP-015 | F09, F10, F31 | Runtime ownership boundaries | cross_spec_mismatch | high | appendix_specified | The authority and API model now states that the daemon is the live orchestration authority, the database is the durable canonical record, and CLI/web clients should talk to the daemon API over HTTPS with a runtime-generated cookie. | Fold the authority model into canonical runtime, DB, lifecycle, CLI, and automation docs and remove older DB-truth-source shorthand. |
| GAP-016 | F01, F35 | Parent/child constraint schema | likely_new_schema | high | in_review | V2 YAML adds parent/child constraint fields, but example constraint patterns and validation rules still need more depth. | Add explicit examples and validation rules in later schema or implementation notes. |
| GAP-017 | F06, F35 | Override conflict semantics | needs_decision | medium | resolved_in_principle | The override conflict semantics note now defines merge modes, field-level defaults, conflict classes, compile-failure behavior, and examples. | Fold the rules into implementation-grade compilation logic and YAML docs. |
| GAP-018 | F17, F19 | Supersession cutover timing | underspecified | medium | appendix_specified | The cutover policy note now defines authoritative vs candidate lineage, cutover scope, old-run handling, rollback semantics, and DB/CLI implications. | Fold the cutover model into canonical runtime/git/DB notes and align current-state views with authoritative lineage semantics. |
| GAP-019 | F31, F36 | Hidden-state audit checklist | missing_artifact | medium | resolved_in_principle | The auditability checklist now provides a concrete no-hidden-state review artifact. | Use it during v2 review and implementation design. |
| GAP-020 | F28 | Summary taxonomy | needs_decision | medium | implementation_open | Summary storage exists, but summary types/scopes need a stronger catalog. | Fold the state value catalog into DB/CLI/runtime implementation details. |
| GAP-021 | F27 | Source role taxonomy | needs_decision | medium | implementation_open | Source lineage exists, but source role categories need to be frozen. | Fold the state value catalog into compilation lineage and DB implementation details. |
| GAP-022 | F13 | Idle escalation semantics | underspecified | medium | in_review | V2 runtime/lifecycle docs now describe bounded nudge escalation, but exact thresholds and terminal actions still depend on policy details. | Add runtime policy defaults or a focused idle-escalation appendix. |
| GAP-023 | F14 | Child session merge-back semantics | underspecified | medium | resolved_in_principle | The child-session merge-back contract now defines the return artifact, validation, parent ownership, and DB/CLI implications. | Fold the contract into final runtime/DB implementation details. |
| GAP-024 | F17 | Branch naming canonicalization | needs_decision | medium | open | V2 git spec requires a deterministic branch rule but intentionally leaves the exact canonical pattern unfrozen. | Freeze branch naming scheme before implementation. |
| GAP-025 | F29, F30 | Docs/provenance ordering | needs_decision | medium | resolved_in_principle | V2 YAML/lifecycle/runtime/git docs now align on provenance before docs before finalize. | Confirm whether any project-policy overrides are allowed and bounded. |
| GAP-026 | F16 | Manual tree + auto tree interaction | underspecified | medium | open | Manual tree construction exists as a requirement, but mixed-mode behavior with auto decomposition is not defined. | Define manual/automatic coexistence rules. |
| GAP-027 | F11 | Operator mutation safety boundaries | underspecified | medium | in_review | V2 CLI clarifies read-only vs mutable classes, but concrete guardrails for destructive or stateful commands still need deeper policy. | Define approval/guard requirements in implementation-facing ops docs. |
| GAP-028 | F03, F27 | Compilation failure handling | underspecified | medium | appendix_specified | The compile failure persistence note now defines compile stages, failure classes, durable failure data, and a recommended `compile_failures` model. | Fold the failure model into canonical DB/lifecycle/CLI docs and decide whether `COMPILE_FAILED` is first-class in the lifecycle catalog. |
| GAP-029 | F02, F19 | Old-version active run handling | underspecified | medium | open | Supersession and cutover are clearer, but active runs on superseded versions are still not fully handled. | Add explicit active-old-run cancellation/recovery policy. |
| GAP-030 | F08 | Invalid dependency graph handling | underspecified | medium | open | Valid dependency types are known, but graph invalidity checks need fuller treatment. | Add graph validation rules and error handling. |

---

## Contradiction Watch List

These are not fully confirmed contradictions yet, but they are areas likely to drift unless frozen explicitly.

## C01. Review/testing/docs as hooks vs explicit tasks

There is a risk of the system modeling these in both ways inconsistently.

Potential contradiction:

- one spec treats them as explicit tasks
- another spec treats them as hook insertions

Needed resolution:

- choose a canonical default model and define where hook-driven insertion is allowed

## C02. Session-owned loop vs supervisor-owned loop

The runtime aims to be CLI-driven by AI sessions, but some logic may implicitly assume an external orchestration supervisor.

Potential contradiction:

- AI loop owns cursor progression
- external runtime owns cursor progression

Needed resolution:

- freeze actor ownership per state transition

## C03. Project policy YAML vs runtime-only policy

It is still unclear which runtime behaviors belong in compiled YAML versus operational runtime config.

Potential contradiction:

- policy treated as immutable workflow input in one place
- policy treated as live runtime setting elsewhere

Needed resolution:

- define compile boundary clearly

## C04. Semantic default ladder vs generic ladder

The design values configurable hierarchy, but the built-in library may become too semantically coupled to `epic/phase/plan/task`.

Potential contradiction:

- generic hierarchy promised
- semantic hierarchy baked in too deeply

Needed resolution:

- define generic substrate and semantic defaults separately

---

## Remaining True Open Gaps

These are the items that still look like real design gaps rather than mostly implementation-detail follow-ups.

- `GAP-005` child materialization and scheduling
- `GAP-006` hook expansion algorithm
- `GAP-012` pause/failure/workflow event persistence decision
- `GAP-016` deeper parent/child constraint examples and validation rules
- `GAP-022` idle escalation defaults if you want them frozen before coding
- `GAP-023` child-session merge-back data contract
- `GAP-026` manual-tree and auto-tree coexistence
- `GAP-029` old-version active-run handling
- `GAP-030` invalid dependency-graph handling

Everything else is mostly:

- resolved in principle by the spec package
- intentionally left for implementation-grade detail
- or waiting for a bounded product-scope choice

---

## Status Meaning

Use these statuses consistently:

- `open`: still a meaningful design gap that needs more spec work
- `in_review`: mostly understood, but still needs one more design decision or confirming pass
- `resolved_in_principle`: spec-level answer exists and should now be folded into implementation-facing docs
- `implementation_open`: design direction is good enough, but exact behavior or structure must be finalized during implementation planning
- `deferred`: intentionally left out of the first implementation scope

---

## Missing Artifact List

The following artifact types are still likely useful, but the matrix is no longer blocked on all of them.

### Strongly recommended next artifacts

- canonical v2 update pass that references the focused appendices
- child scheduling / materialization note
- hook expansion algorithm note
- dependency graph validation note
- manual-vs-auto tree interaction note

### Likely future dedicated specs or appendices

- validation result model appendix
- review result model appendix
- test result model appendix
- implementation-time authority/cutover modeling note if needed
- operator mutation guardrails note
- pause/workflow event persistence note

---

## Priority Resolution Order

The recommended order for resolving the current gaps is:

1. write child materialization and scheduling note
2. write hook expansion algorithm note
3. decide whether pause/workflow events need dedicated tables
4. write dependency graph validation note
5. write manual-vs-auto tree interaction note
6. freeze branch naming pattern before implementation
7. decide whether authoritative-version modeling needs an explicit DB structure

---

## Recommended Next Review Cycle

After the next 2-3 planning docs are written, rerun this matrix and update:

- feature statuses
- artifact states
- gap priorities
- contradiction resolutions

The next review should especially verify:

- whether the v2 docs are internally consistent after the appendix set
- whether the remaining open gaps are truly implementation details or still design gaps
- whether isolated environments are intentionally deferred or need bounded first-class treatment
- whether recently folded-in appendix decisions remove the need for any remaining dedicated appendix docs

---

## Exit Criteria

This gap matrix should be considered canonical enough when:

- duplicate and stale gap rows are removed
- statuses distinguish design-open from implementation-open
- true remaining design gaps are isolated clearly
- likely contradictions are named
- the next resolution order is explicit

At that point, the design work can proceed from broad inventory into targeted closure of the remaining open gaps and then implementation.
