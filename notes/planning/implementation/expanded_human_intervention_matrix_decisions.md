# Expanded Human Intervention Matrix Decisions

## Summary

Feature `72_F13_expanded_human_intervention_matrix` now adds a bounded unified intervention surface without introducing a separate intervention table.

## Decisions

1. Human intervention is now exposed through one daemon-owned catalog per node rather than only through pause-specific reads.
   Current implemented intervention kinds:
   - `pause_approval`
   - `child_reconciliation`
   - `merge_conflict`
   - `session_recovery`
   - `cutover_review` as a read-only attention item

2. Intervention application is daemon-owned and explicit.
   Current implemented actions:
   - `approve_pause`
   - `preserve_manual`
   - `abort_merge`
   - `resolve_conflict`
   - `resume_session`

3. This slice does not add a new `interventions` table.
   The current bounded decision is to reuse existing durable source-of-truth tables plus `workflow_events` for intervention audit. This keeps the intervention layer narrow while the runtime still relies on existing pause, reconciliation, merge-conflict, and recovery state families.

4. The canonical CLI/API surface for this slice is:
   - `GET /api/nodes/{node_id}/interventions`
   - `POST /api/nodes/interventions/apply`
   - `ai-tool node interventions --node <id>`
   - `ai-tool node intervention-apply --node <id> --kind <kind> --action <action>`

5. The current intervention model is intentionally broader than pause approval but not yet universal.
   Remaining deferred families:
   - direct rebuild-decision apply surfaces
   - direct cutover-review apply surfaces
   - richer hybrid reconciliation decisions beyond `preserve_manual`
   - merge-decision families beyond `abort_merge` and explicit conflict resolution

6. Flow 13 should now be treated as partially closed through a unified intervention entrypoint rather than a pause-only exception path.

## Testing

This slice is covered by:

- unit intervention-catalog and apply tests
- daemon endpoint tests for pause approval and merge-conflict abort
- CLI round-trip coverage for pause approval through the unified intervention command
- Flow 13 contract coverage
- performance coverage for repeated intervention-catalog lookup

## Performance

Intervention catalog reads are expected to remain cheap because they aggregate from already-existing durable state rather than materializing a second intervention ledger.
