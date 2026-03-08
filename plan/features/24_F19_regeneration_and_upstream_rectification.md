# Phase F19: Regeneration And Upstream Rectification

## Goal

Support subtree regeneration and ancestor rebuild without premature cutover.

## Scope

- Database: rebuild events, candidate lineage, rectification progress.
- CLI: regenerate, rectify-upstream, and rebuild-history commands.
- Daemon: candidate lineage creation, subtree regeneration, and rectification.
- YAML: rectification tasks and rebuild policies.
- Prompts: regenerated execution and parent rectify prompts.
- Tests: exhaustive candidate-lineage safety, sibling reuse, rectification failure, and no-premature-cutover coverage.
- Performance: benchmark rebuild and rectification over multi-node trees.
- Notes: update rectification/cutover notes if implementation tightens scope rules.
