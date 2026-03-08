# Open Questions

## Purpose

Track the highest-value unresolved questions exposed by the current pseudocode package so follow-on work can target actual ambiguity instead of rephrasing settled behavior.

---

## High-priority questions

### OQ-001: Is `COMPILE_FAILED` a first-class lifecycle state?

Why it matters:

- compile failure is now explicit in pseudocode and lifecycle normalization
- implementation could still model it as derived blocked state instead

Affected artifacts:

- `modules/compile_workflow.md`
- `state_machines/node_lifecycle.md`

Recommended direction:

- treat as first-class unless DB simplicity becomes a hard constraint

---

### OQ-002: What is the first canonical branch naming rule?

Why it matters:

- rectification and auditability need deterministic branch identity

Affected artifacts:

- `modules/rectify_node_from_seed.md`
- `modules/regenerate_node_and_descendants.md`

Recommended direction:

- freeze one simple derivable scheme before coding

---

### OQ-003: Should cutover support any bounded local scope in v1?

Why it matters:

- pseudocode currently assumes upstream lineage cutover by default
- supporting smaller scopes early could complicate authority reasoning

Affected artifacts:

- `modules/finalize_lineage_cutover.md`
- `state_machines/lineage_authority.md`

Recommended direction:

- default to upstream-only first

---

### OQ-004: Should `code_entity_observations` exist in the first provenance implementation?

Why it matters:

- provenance matching is now explicit
- observation history improves auditability but adds schema complexity

Affected artifacts:

- `modules/update_provenance_for_node.md`

Recommended direction:

- optional for v1 unless provenance is a flagship feature immediately

---

### OQ-005: How should low-confidence provenance matches be handled?

Why it matters:

- creating a new anchor is safer
- storing low-confidence inferred continuity may still be useful

Affected artifacts:

- `modules/update_provenance_for_node.md`

Recommended direction:

- prefer new anchor when confidence is weak

---

### OQ-006: Can unchanged children ever be structurally reused automatically after a layout change?

Why it matters:

- full parent replan is safer
- selective reuse could reduce churn but increases authority complexity

Affected artifacts:

- `modules/materialize_layout_children.md`
- `state_machines/parent_child_authority.md`

Recommended direction:

- require explicit replan/reconciliation first

---

### OQ-007: Are merge conflict resolutions normal compiled subtasks or special rectification substates?

Why it matters:

- this changes runtime ownership, CLI surfaces, and persistence shape

Affected artifacts:

- `modules/rectify_node_from_seed.md`

Recommended direction:

- likely special rectification substates first, then compiled-task integration later if needed
