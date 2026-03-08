# Flow 10: Regenerate And Rectify

## Purpose

Create a new node version or rebuild an upstream subtree when prompts, layouts, overrides, or child results require a structural or behavioral change.

## Covers journeys

- regenerate a node after prompt or policy change
- rectify upstream after downstream findings
- rebuild without mutating old versions in place

## Entry conditions

- a change request affects an existing authoritative node or subtree

## Task flow

1. capture the regeneration or rectification trigger
2. determine impacted node versions and subtree scope
3. create superseding node version(s)
4. preserve prior lineage rather than mutating old versions
5. determine reusable vs superseded child outputs
6. recompile affected workflows
7. handle old active runs explicitly
8. rebuild or rematerialize affected descendants
9. perform ordered reconciliation and merge where required
10. cut over authoritative lineage when safe

## Required subtasks

- `capture_rebuild_trigger`
- `determine_impacted_scope`
- `create_superseding_versions`
- `classify_reusable_outputs`
- `recompile_affected_workflows`
- `handle_old_active_runs`
- `rebuild_descendants_if_needed`
- `reconcile_and_cut_over`

## Required capabilities

- `ai-tool node regenerate ...`
- `ai-tool node rectify-upstream ...`
- node supersession/versioning
- cutover policy
- active-old-run handling
- rebuild event history

## Durable outputs

- new node version lineage
- rebuild event records
- authoritative/candidate cutover records
- reuse/supersession decisions
- merge or rectification summaries

## Failure cases that must be supported

- active old run conflicts with cutover
- authoritative target ambiguity
- rebuild introduces child-layout conflict
- upstream merge conflict during rectification

## Completion rule

The system exposes one authoritative lineage while preserving full history of what was rebuilt, reused, superseded, and cut over.
