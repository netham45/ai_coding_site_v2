# State Machine: Parent Child Authority

## Purpose

Normalize how the parent child-set authority mode changes over time so structural reconciliation and regeneration do not rely on implicit assumptions.

---

## Source notes

Primary:

- `notes/manual_vs_auto_tree_interaction.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/state_value_catalog.md`

Supporting:

- `notes/git_rectification_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`

---

## Canonical authority modes

- `manual`
- `layout_authoritative`
- `hybrid`

These modes align with [state_value_catalog.md](/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2/notes/state_value_catalog.md).

---

## Mode meanings

- `manual`: child set exists without an authoritative layout driving structural replacement
- `layout_authoritative`: current child set is governed by an authoritative layout
- `hybrid`: the child set originated from layout or mixed sources but now includes manual structural edits requiring explicit reconciliation

---

## Core transitions

- `manual -> hybrid`
  Condition: layout-driven materialization is introduced without explicit manual adoption semantics

- `layout_authoritative -> hybrid`
  Condition: manual child add/remove/reorder/edit changes the child set after layout materialization

- `hybrid -> layout_authoritative`
  Condition: explicit reconciliation adopts a layout as authoritative over the resulting child set

- `hybrid -> manual`
  Condition: explicit reconciliation discards layout authority and preserves a fully manual child set

- `manual -> layout_authoritative`
  Condition: explicit operator or policy action adopts a layout as the structural source of truth

---

## Transition guards

- no silent `hybrid -> layout_authoritative`
- no silent `hybrid -> manual`
- no silent `layout_authoritative` structural replacement after manual edits
- no layout update should mutate a `manual` child set without explicit adoption/reconciliation

---

## Consequences by mode

### `manual`

- scheduling and dependency legality still apply normally
- regeneration preserves manual structure unless explicit structural change is requested

### `layout_authoritative`

- layout updates may drive child materialization and structural regeneration

### `hybrid`

- automatic structural regeneration is blocked
- reconciliation decision is required before structure changes proceed

---

## Pseudotests

### `manual_edit_of_layout_child_set_enters_hybrid_mode`

Given:

- child set was layout-authoritative
- a manual structural edit occurs

Expect:

- authority mode becomes `hybrid`

### `hybrid_mode_blocks_silent_layout_regeneration`

Given:

- parent authority mode is `hybrid`

Expect:

- structural layout regeneration cannot proceed automatically

### `explicit_reconciliation_can_restore_layout_authority`

Given:

- parent authority mode is `hybrid`
- user or policy explicitly adopts reconciled layout

Expect:

- mode may return to `layout_authoritative`
