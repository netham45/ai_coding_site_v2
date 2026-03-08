# Flow 11: Finalize And Merge

## Purpose

Finalize completed node work and merge child or node outputs into the correct parent or base branch with durable audit history.

## Covers journeys

- finalize a completed node
- merge children into a parent
- approve merge to parent or base

## Entry conditions

- required work is complete
- required quality gates have passed or been explicitly overridden

## Task flow

1. confirm required children and gates are complete
2. reset the parent or target branch to its seed if required by reconcile policy
3. apply ordered child merges
4. detect and persist conflicts
5. resolve or pause on conflicts according to policy
6. record final commit metadata
7. update node lifecycle state to complete/finalized
8. if merge to parent or base is gated, wait for approval before final cutover

## Required subtasks

- `confirm_finalize_preconditions`
- `reset_target_to_seed_if_required`
- `apply_ordered_merges`
- `persist_merge_events`
- `handle_conflicts`
- `record_final_commit`
- `transition_node_to_finalized`
- `apply_merge_cutover_if_approved`

## Required capabilities

- `ai-tool git merge-current-children ...`
- `ai-tool git finalize-node ...`
- `ai-tool merge approve ...`
- merge conflict persistence
- final commit tracking
- merge audit views

## Durable outputs

- merge events
- conflict records
- final commit ID
- finalize summary
- updated node lifecycle state

## Failure cases that must be supported

- required child missing or incomplete
- required quality gate not passed
- merge conflict
- gated merge approval denied or deferred

## Completion rule

Users can inspect what was merged, in what order, onto which target, under which approvals, and with what final commit outcome.
