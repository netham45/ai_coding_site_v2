# Turnkey Quality Gate Finalize Chain Decisions

## Scope

F21/F22/F23/F29 follow-on work adds one daemon-owned turnkey quality chain over the existing validation, review, testing, provenance, and docs slices.

## Decisions

1. The canonical turnkey operator surface is now `node quality-chain --node <id>`, backed by `POST /api/nodes/{node_id}/quality-chain/run`.
2. This slice deliberately reuses the existing built-in gate evaluators instead of introducing a parallel quality-engine implementation. The quality-chain helper starts and completes the current built-in gate subtasks with deterministic success payloads and then routes through the existing `workflow advance` logic.
3. Provenance refresh and docs build remain daemon-owned late-chain actions after the gate stages succeed. They are executed immediately after the active run reaches `COMPLETE`, then a durable final node summary is written to `summaries` with `summary_type = node` and `summary_path = summaries/final.md`.
4. The current turnkey chain does not require changing the default compiled node task ladder. It provides one canonical end-to-end operator path without forcing every default node compile to include late-chain task expansion immediately.
5. The final quality summary intentionally uses the existing `node` summary type because the current durable summary schema does not define a separate `final` summary type.

## Deferred Work

- The late-chain steps are daemon-owned orchestration, not yet compiled workflow subtasks for every default node kind.
- Live git finalize/merge execution remains out of scope here and still belongs to the later git execution slice.
- Broader review/testing customization beyond the deterministic built-in success path remains governed by the existing review/testing command surfaces.
