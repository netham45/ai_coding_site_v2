# Rectification And Cutover Pseudotests

## Purpose

These pseudotests validate rebuild, authority, cutover, and provenance behaviors that sit above the runtime spine.

Covered modules and state machines:

- `regenerate_node_and_descendants(...)`
- `rectify_node_from_seed(...)`
- `finalize_lineage_cutover(...)`
- `update_provenance_for_node(...)`
- `state_machines/lineage_authority.md`
- `state_machines/parent_child_authority.md`

---

## Candidate lineage

### `candidate_lineage_stays_non_authoritative_during_rebuild`

Scenario:

- a changed node creates a superseding candidate lineage
- rebuild is still in progress

Action:

- query lineage authority while candidate rebuild continues

Expected durable effects:

- candidate lineage is queryable
- authoritative lineage selector still points to the old scope

Expected operator-visible results:

- system distinguishes latest created from authoritative

### `failed_candidate_does_not_contaminate_parent_or_dependency_resolution`

Scenario:

- candidate child lineage fails before cutover

Action:

- query parent child results and dependency evaluation

Expected durable effects:

- failed candidate remains historical only
- old authoritative child lineage remains the one consumed

Expected operator-visible results:

- failure is visible without being treated as current effective child state

---

## Rectification

### `rectification_uses_authoritative_child_finals_only`

Scenario:

- one child has an authoritative final
- a newer candidate child exists but is not cut over

Action:

- run `rectify_node_from_seed(node_version_id)`

Expected durable effects:

- merge planning uses only authoritative child finals

Expected operator-visible results:

- merge input summary shows why the candidate child was excluded

### `rectification_stops_before_quality_gates_when_merge_conflict_occurs`

Scenario:

- deterministic child merge order reaches a conflicting child commit

Action:

- run `rectify_node_from_seed(node_version_id)`

Expected durable effects:

- merge conflict record is written
- validation/review/testing/provenance/docs do not proceed

Expected operator-visible results:

- current blocking conflict is inspectable

---

## Cutover

### `cutover_requires_full_scope_stability_by_default`

Scenario:

- changed node and descendants succeeded
- one required ancestor rectification is still incomplete

Action:

- run `finalize_lineage_cutover(logical_node_id, candidate_root_version_id)`

Expected durable effects:

- no authority switch occurs

Expected operator-visible results:

- cutover reports `not_ready`

### `user_gated_cutover_pauses_before_authority_switch`

Scenario:

- candidate scope is stable
- policy requires explicit approval

Action:

- run `finalize_lineage_cutover(...)`

Expected durable effects:

- pause event is recorded
- authority selector remains unchanged

Expected operator-visible results:

- candidate is ready but awaiting approval

### `successful_cutover_switches_authority_then_supersedes_old_scope`

Scenario:

- candidate scope is stable
- no unresolved conflicts or gates remain

Action:

- run `finalize_lineage_cutover(...)`

Expected durable effects:

- candidate scope becomes authoritative
- replaced scope becomes superseded
- cutover completion event is persisted

---

## Provenance

### `provenance_prefers_exact_match_over_heuristic_match`

Scenario:

- an extracted entity has both an exact structural match and a weaker heuristic candidate

Action:

- run `update_provenance_for_node(node_version_id)`

Expected durable effects:

- exact anchor is reused
- confidence is `high`

Expected operator-visible results:

- match explanation cites exact evidence rather than heuristic evidence

### `provenance_exposes_inference_confidence_when_rename_or_move_is_assumed`

Scenario:

- no exact match exists
- a strong rename or move candidate exists

Action:

- run `update_provenance_for_node(node_version_id)`

Expected durable effects:

- match reason and confidence are persisted

Expected operator-visible results:

- lineage is shown as inferred rather than certain

---

## Structural authority

### `hybrid_child_authority_blocks_silent_regeneration`

Scenario:

- parent child authority mode is `hybrid`
- layout update is requested

Action:

- attempt `materialize_layout_children(...)` or regeneration that would alter structure

Expected durable effects:

- no structural authority change occurs automatically

Expected operator-visible results:

- explicit reconciliation is required
