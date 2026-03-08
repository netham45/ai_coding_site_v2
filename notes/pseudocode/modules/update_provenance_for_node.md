# Module: `update_provenance_for_node(...)`

## Purpose

Refresh provenance and rationale mappings for one node version by extracting current code entities, matching them against durable entity anchors, and recording confidence-aware identity continuity.

---

## Source notes

Primary:

- `notes/provenance_identity_strategy.md`

Supporting:

- `notes/git_rectification_spec_v2.md`
- `notes/auditability_checklist.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `node_version_id`
- current working tree or final commit snapshot for the node
- existing code entity anchors
- existing code relations and prior provenance history

---

## Required state

- the node's code snapshot is analyzable
- current entity anchors are queryable
- provenance tables or equivalent durable stores are writable

---

## Outputs

- updated entity matches
- new entity anchors where safe match is not available
- confidence-aware provenance updates
- provenance summary for docs and audit surfaces

---

## Durable writes

- code-entity matches and updates
- new code-entity rows where required
- match confidence and match rationale
- node-entity change records
- provenance update summary

---

## Decision algorithm

```text
function update_provenance_for_node(node_version_id):
  extracted_entities = extract_entities_from_node_snapshot(node_version_id)
  existing_entities = load_existing_entity_anchors()
  updates = []

  for observed in extracted_entities:
    exact_match = find_exact_structural_match(observed, existing_entities)
    if exact_match is not null:
      updates.append(build_entity_update(observed, exact_match, confidence = "high", reason = "exact_match"))
      continue

    heuristic_match = find_strong_rename_or_move_candidate(observed, existing_entities)
    if heuristic_match is not null:
      updates.append(build_entity_update(observed, heuristic_match, confidence = "medium", reason = "heuristic_match"))
      continue

    updates.append(build_new_entity_anchor(observed, confidence = "high", reason = "new_entity"))

  persist_provenance_updates(node_version_id, updates)
  persist_provenance_summary(node_version_id, updates)
  return ProvenanceResult(status = "ok", update_count = len(updates))
```

---

## Matching strategy

Apply matching in this order:

1. exact structural identity match
2. strong rename or move candidate
3. no safe match, create new entity anchor

When confidence is weak:

- prefer a new entity over false certainty
- preserve inferred status explicitly if a heuristic match is accepted

---

## Confidence model

Use categorical confidence for first-pass pseudocode:

- `high`
- `medium`
- `low`

Recommended default:

- exact match: `high`
- strong rename or move heuristic: `medium`
- weak heuristic: avoid using unless policy explicitly allows it

---

## Failure paths

### Extraction failure

- preserve failure summary
- do not claim provenance success

### Ambiguous heuristic match

- do not silently pick one candidate
- either create a new entity or record low-confidence inference explicitly according to policy

### Persistence failure

- no partial provenance result should be presented as fully complete

---

## Auditability rule

If identity continuity is inferred rather than proven:

- record why
- record the confidence level
- make that visible to CLI and docs surfaces

The system should be able to explain why an entity was considered the same as a prior one.

---

## CLI-visible expectations

Operators should be able to inspect:

- entity current identity
- why a match was made
- confidence level
- whether a relation is inferred rather than exact

---

## Open questions

- whether the first implementation should add `code_entity_observations` immediately or defer it
- whether low-confidence inferred matches should be stored at all or always converted into new anchors

---

## Pseudotests

### `preserves_identity_on_exact_match`

Given:

- entity type, name, file path, and structural fingerprint align

Expect:

- existing entity anchor is reused with `high` confidence

### `records_medium_confidence_for_strong_rename_or_move`

Given:

- exact match fails
- rename or move evidence is strong

Expect:

- existing anchor may be reused
- confidence and heuristic reason are persisted

### `creates_new_entity_when_match_is_unsafe`

Given:

- no safe exact or strong heuristic match exists

Expect:

- new entity anchor is created
- false continuity is not claimed
