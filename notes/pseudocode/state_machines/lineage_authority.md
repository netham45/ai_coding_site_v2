# State Machine: Lineage Authority

## Purpose

Normalize the authority relationship between old lineage, candidate lineage, and superseded lineage so rebuild and cutover behavior stays explicit and auditable.

---

## Source notes

Primary:

- `notes/cutover_policy_note.md`
- `notes/git_rectification_spec_v2.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/state_value_catalog.md`
- `notes/parent_failure_decision_spec.md`

---

## Canonical lineage scopes

Use these conceptual scope values for first-pass pseudocode:

- `candidate`
- `authoritative`
- `superseded`
- `failed_candidate`

This extends the current lineage-scope concept in [state_value_catalog.md](/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2/notes/state_value_catalog.md) so candidate rebuild outcomes are explicit.

---

## Scope meanings

- `authoritative`: current effective version used for dependency evaluation, operator current views, and future rebuild baselines
- `candidate`: newer durable lineage under rebuild or pre-cutover validation, not yet current truth
- `failed_candidate`: candidate lineage that failed before authority transfer
- `superseded`: historical lineage replaced by a newer authoritative lineage

---

## Core transitions

- `authoritative -> authoritative`
  Condition: no rebuild or cutover occurs

- `authoritative + create_superseding_version -> candidate`
  Condition: regeneration or rectification begins for a new lineage

- `candidate -> authoritative`
  Condition: required rebuilt scope is stable and cutover succeeds

- `candidate -> failed_candidate`
  Condition: candidate lineage fails before cutover

- `authoritative -> superseded`
  Condition: successful cutover marks replaced lineage historical

- `failed_candidate -> candidate`
  Condition: explicit retry or regeneration from failure path creates a new candidate attempt

---

## Transition guards

- no `candidate -> authoritative` before required scope is stable
- no `candidate -> authoritative` while unresolved merge conflicts remain
- no `candidate -> authoritative` while blocking user gate remains unresolved
- no dependency evaluation against `candidate` unless explicitly in preview/review mode
- no silent `authoritative -> superseded` before cutover record exists

---

## Scope stability rules

Before `candidate -> authoritative`, verify at minimum:

- changed node completed successfully
- required regenerated descendants completed successfully
- required ancestor rectifications completed successfully
- required quality gates succeeded
- required final commits exist
- no unresolved merge conflicts remain
- no unresolved user gate remains

If any of these fail:

- candidate remains non-authoritative

---

## Old-lineage interaction

- old authoritative lineage remains authoritative during candidate rebuild
- failed candidates do not replace old authority
- parent reconciliation and dependency checks continue to use authoritative lineage until cutover

---

## Illegal or suspicious transitions

- `failed_candidate -> authoritative`
- `candidate -> superseded` without either failure classification or cutover replacement semantics
- `superseded -> authoritative`

These should require an explicit exceptional recovery or administrative intervention path.

---

## Pseudotests

### `candidate_does_not_replace_authority_before_cutover`

Given:

- a new candidate lineage exists

Expect:

- old authoritative lineage remains current until explicit cutover

### `failed_candidate_preserves_old_authority`

Given:

- candidate lineage fails before cutover

Expect:

- old authoritative lineage remains active
- failed candidate remains historical only

### `dependency_evaluation_uses_authoritative_not_latest_created`

Given:

- latest created version is candidate
- older version is still authoritative

Expect:

- dependency resolution uses the authoritative version
