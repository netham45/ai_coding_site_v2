# Phase F05-S2: Prompt Pack Authoring

## Goal

Author the full built-in prompt pack as implementation assets rather than placeholders.

## Scope

- Database: ensure prompt-template identity and prompt history can reference authored assets cleanly.
- CLI: expose prompt inspection against real authored prompt files.
- Daemon: load, render, and issue authored prompt assets reliably.
- YAML: bind built-in tasks/subtasks/reviews/testing/docs/runtime behaviors to concrete prompt assets.
- Prompts: author the full prompt pack, including decomposition, execution, recovery, missed-step, pause, review, testing, docs, and child-session prompts.
- Tests: exhaustively validate prompt asset loading, placeholder coverage, rendering compatibility, and prompt-to-stage contract alignment.
- Performance: benchmark prompt-pack load and render costs.
- Notes: keep prompt library notes synchronized with actual authored assets.
