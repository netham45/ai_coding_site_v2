# Rectification And Cutover Results

## Suite summary

- `pass`: 10
- `partial`: 0
- `fail`: 0

---

### `candidate_lineage_stays_non_authoritative_during_rebuild`

- Verdict: `pass`
- Simulated inputs:
  - logical node `LN-400`
  - old authoritative `V1`
  - new candidate `V2` under rebuild
- Simulated YAML reads:
  - none after candidate compile; authority uses lineage metadata
- Simulated DB reads:
  - authoritative-version selector
  - latest created version
  - rebuild scope
- Logic path:
  - `regenerate_node_and_descendants` creates superseding version
  - marks lineage scope `candidate`
  - `lineage_authority` state machine forbids candidate replacing authority pre-cutover
- Simulated DB writes:
  - candidate lineage summary
  - rebuild event
- Forbidden-effects check:
  - authority selector remains on old lineage

### `failed_candidate_does_not_contaminate_parent_or_dependency_resolution`

- Verdict: `pass`
- Simulated inputs:
  - candidate child lineage fails before cutover
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - authoritative child selector
  - candidate failure history
  - parent child result collection
- Logic path:
  - `lineage_authority` transitions candidate to `failed_candidate`
  - `collect_child_results` still resolves old authoritative child
  - dependency evaluation continues to use authoritative lineage
- Simulated DB writes:
  - failed candidate marker
  - failure history
- Forbidden-effects check:
  - parent does not consume failed candidate as current child result

### `rectification_uses_authoritative_child_finals_only`

- Verdict: `pass`
- Simulated inputs:
  - one authoritative child final commit
  - newer candidate child version exists
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - branch metadata
  - authoritative child results
  - final commits
- Logic path:
  - `rectify_node_from_seed` calls `collect_child_results`
  - only authoritative child final is used to compute merge order
- Simulated DB writes:
  - rectification start event
  - merge events for authoritative children only
- Forbidden-effects check:
  - candidate child final excluded from merge input

### `rectification_stops_before_quality_gates_when_merge_conflict_occurs`

- Verdict: `pass`
- Simulated inputs:
  - second child merge causes conflict
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - branch metadata
  - merge order
  - child final commits
- Logic path:
  - branch reset to seed
  - first merge clean
  - second merge conflicts
  - merge conflict recorded
  - rectification returns early
- Simulated DB writes:
  - rectification start event
  - merge events
  - `merge_conflicts`
- Forbidden-effects check:
  - validation/review/testing/provenance/docs do not run after conflict

### `cutover_requires_full_scope_stability_by_default`

- Verdict: `pass`
- Simulated inputs:
  - changed node and descendants succeeded
  - ancestor rebuild still incomplete
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - candidate scope
  - status of rebuilt nodes in scope
  - current authoritative scope
- Logic path:
  - `finalize_lineage_cutover` records precheck
  - `scope_is_stable(candidate_scope) == false`
  - returns `not_ready`
- Simulated DB writes:
  - cutover precheck event
- Forbidden-effects check:
  - no authority selector mutation
  - old scope not superseded

### `user_gated_cutover_pauses_before_authority_switch`

- Verdict: `pass`
- Simulated inputs:
  - candidate scope stable
  - approval gate required
- Simulated YAML reads:
  - cutover policy / approval requirement
- Simulated DB reads:
  - candidate scope status
  - unresolved user gate
- Logic path:
  - cutover precheck succeeds
  - unresolved user gate detected
  - `pause_for_user` invoked
- Simulated DB writes:
  - cutover precheck event
  - pause event
- Forbidden-effects check:
  - no authority switch performed

### `successful_cutover_switches_authority_then_supersedes_old_scope`

- Verdict: `pass`
- Simulated inputs:
  - stable candidate scope
  - no unresolved conflicts
  - no unresolved gate
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - candidate scope
  - current authoritative scope
- Logic path:
  - `finalize_lineage_cutover` enters transaction
  - marks candidate authoritative
  - marks replaced scope superseded
  - persists cutover-complete event
- Simulated DB writes:
  - authority selector update
  - supersession update on old scope
  - cutover-complete event
- Forbidden-effects check:
  - no split authority left behind on success path

### `provenance_prefers_exact_match_over_heuristic_match`

- Verdict: `pass`
- Simulated inputs:
  - observed entity has exact structural match and weaker rename candidate
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - `code_entities`
  - prior provenance anchors
  - relations neighborhood if needed
- Logic path:
  - `update_provenance_for_node` extracts entities
  - exact structural match found first
  - heuristic branch skipped
- Simulated DB writes:
  - updated provenance link
  - `node_entity_changes`
  - summary with `confidence = high`, `reason = exact_match`
- Forbidden-effects check:
  - no weaker heuristic chosen over exact match

### `provenance_exposes_inference_confidence_when_rename_or_move_is_assumed`

- Verdict: `pass`
- Simulated inputs:
  - no exact match
  - strong rename/move candidate exists
- Simulated YAML reads:
  - none
- Simulated DB reads:
  - entity anchors
  - structural fingerprints
  - relation neighborhood
- Logic path:
  - exact match lookup fails
  - strong heuristic match found
  - update persisted with explicit confidence and reason
- Simulated DB writes:
  - provenance update
  - confidence/rationale metadata
  - provenance summary
- Forbidden-effects check:
  - inferred continuity is not presented as exact

### `hybrid_child_authority_blocks_silent_regeneration`

- Verdict: `pass`
- Simulated inputs:
  - parent authority mode `hybrid`
  - layout-driven regeneration requested
- Simulated YAML reads:
  - updated layout
- Simulated DB reads:
  - parent child authority mode
  - current child set
- Logic path:
  - `parent_child_authority` state machine blocks automatic structure mutation
  - `materialize_layout_children` returns reconciliation requirement
  - regeneration cannot proceed silently
- Simulated DB writes:
  - reconciliation-required event
- Forbidden-effects check:
  - no automatic structural replacement
