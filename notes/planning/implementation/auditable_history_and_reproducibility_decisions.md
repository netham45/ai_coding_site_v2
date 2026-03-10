# Auditable History And Reproducibility Decisions

## Scope implemented in this slice

- Added daemon-backed audit reconstruction views for nodes and runs.
- Added CLI read surfaces for node-level and run-level audit inspection.
- Added focused unit, integration, CLI, and performance coverage for audit reconstruction.

## Key implementation decisions

- This slice does not add a new audit table. Reconstruction is built by aggregating the existing durable history families that earlier phases already persisted.
- `node audit --node <id>` is the broad operator reconstruction surface. It aggregates node summary, lineage, authoritative workflow state, source lineage, prompt and summary history, quality-gate history, session history, rebuild history, merge history, docs history, and run count.
- `node run audit --run <id>` is the canonical historical-run reconstruction surface. `node run audit --node <id>` is a convenience alias that resolves to the latest run for the node.
- Run-scoped audit snapshots intentionally treat `workflow_events` as optional. A valid run may have no workflow-event rows if it never entered a path that records pause, approval, retry, cancel, or other workflow-control events.
- The audit bundle is a read model only. It is not a second durable authority and should stay derivable from the underlying canonical tables.

## Boundaries kept in place

- Summary history remains driven by successful `summary register`, not by subtask completion alone.
- Prompt history remains driven by prompt delivery, not by workflow compilation.
- Session reconstruction remains bounded to the durable session/session-event model; the audit bundle does not treat tmux state as authoritative history.

## Deferred work

- There is still no single exported "full incident bundle" artifact or archive format; the current slice stops at daemon and CLI aggregation surfaces.
- Broader end-to-end reproducibility scenarios across rebuild, recovery replacement, and merge-conflict resolution remain covered through their local history families rather than a new omnibus flow test.
