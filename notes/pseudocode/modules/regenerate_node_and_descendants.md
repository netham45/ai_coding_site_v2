# Module: `regenerate_node_and_descendants(...)`

## Purpose

Create a superseding candidate lineage for a changed node, regenerate the required descendant subtree, and prepare the rebuilt lineage for upstream rectification and eventual cutover.

---

## Source notes

Primary:

- `notes/git_rectification_spec_v2.md`
- `notes/cutover_policy_note.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/manual_vs_auto_tree_interaction.md`

---

## Inputs

- `changed_node_version_id`
- regeneration trigger reason
- subtree scope policy
- current authoritative lineage selectors

---

## Required state

- changed node version exists
- current authoritative lineage is queryable
- supersession and cutover metadata are writable
- active-run conflict policy is available

---

## Outputs

- superseding candidate node version
- superseding descendant versions where required
- candidate lineage summary
- handoff to upstream rectification flow

---

## Durable writes

- superseding node-version rows
- lineage linkage such as `supersedes_node_version_id`
- candidate lineage markers
- rebuild events
- run-conflict resolution events where applicable

---

## Happy path

```text
function regenerate_node_and_descendants(changed_node_version_id):
  resolve_active_run_conflicts_for_logical_node(changed_node_version_id)

  new_version = create_superseding_node_version(changed_node_version_id)
  mark_lineage_scope(new_version.id, scope = "candidate")

  compile_result = compile_workflow(new_version.id)
  if compile_result.status != "ok":
    return RegenerationResult(status = "compile_failed", node_version_id = new_version.id)

  descendants = determine_required_descendant_regeneration_scope(new_version.id)
  generated_descendants = []

  for descendant in descendants:
    descendant_version = create_superseding_descendant_version(descendant)
    mark_lineage_scope(descendant_version.id, scope = "candidate")
    child_compile = compile_workflow(descendant_version.id)
    if child_compile.status != "ok":
      record_descendant_regeneration_failure(new_version.id, descendant_version.id)
      return RegenerationResult(status = "descendant_compile_failed", node_version_id = new_version.id)
    generated_descendants.append(descendant_version.id)

  persist_candidate_lineage_summary(new_version.id, generated_descendants)
  return RegenerationResult(status = "candidate_lineage_created", node_version_id = new_version.id)
```

---

## Scope rules

- regenerate only the changed node and descendants whose structure or inputs are affected
- reuse unaffected siblings by current authoritative final commit
- do not mark the new lineage authoritative during candidate rebuild

---

## Active-run conflict behavior

Before starting a superseding rebuild:

- detect active runs on the old authoritative version
- pause, cancel, or defer according to policy
- do not allow ambiguous simultaneous authoritative execution paths for one logical node

Recommended default:

- pause or explicitly cancel old active run before conflicting rebuild execution proceeds

---

## Failure paths

### Changed node compile failure

- candidate lineage remains non-authoritative
- old lineage remains authoritative

### Descendant compile failure

- record failure within candidate lineage
- do not cut over

### Scope ambiguity

- if descendant regeneration scope cannot be determined confidently, pause for user or require explicit replanning

---

## Pause/recovery behavior

- candidate lineage state must be durable and resumable
- interrupted regeneration should resume within the candidate lineage, not mutate the old authoritative lineage in place

---

## CLI-visible expectations

Operators should be able to inspect:

- authoritative version
- latest candidate version
- rebuild scope
- whether active-run conflicts were paused, canceled, or deferred

---

## Open questions

- how narrowly descendant regeneration scope can be computed in first implementation without risking hidden omissions
- whether candidate lineage summaries need dedicated tables or can live in rebuild-event history

---

## Pseudotests

### `creates_candidate_lineage_without_early_cutover`

Given:

- a changed node version is regenerated

Expect:

- new version is candidate only
- old lineage remains authoritative until rebuild succeeds

### `preserves_old_authority_when_candidate_compile_fails`

Given:

- superseding node compile fails

Expect:

- old lineage remains authoritative

### `resolves_active_run_conflict_before_conflicting_rebuild_execution`

Given:

- old authoritative version still has an active run

Expect:

- conflict is explicitly resolved before rebuild proceeds
