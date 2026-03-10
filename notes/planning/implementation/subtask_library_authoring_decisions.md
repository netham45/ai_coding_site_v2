# Subtask Library Authoring Decisions

## Packaging choice

This phase freezes the packaging choice explicitly:

- built-in `subtasks/*.yaml` files are the canonical authored subtask catalog
- task definitions still inline subtask payloads during compilation in the current implementation

That is a deliberate staged boundary, not an accident.

## Why this staging was kept

- rewriting task compilation to resolve subtask ids as first-class reusable references would expand the compiler boundary substantially
- the current runtime already compiles and dispatches inline subtask payloads correctly
- the immediate gap was asset quality and verification, not a missing compiler abstraction

## Resulting standard

For this slice, every built-in standalone subtask file must be:

- schema-valid
- bound to existing prompt assets where prompt-bearing
- aligned to a currently supported runtime subtask type
- non-destructive by default
- synthetically compileable into a one-task workflow
- startable by the current runtime without custom hacks

## Safety choice

The standalone `reset_to_seed` built-in no longer embeds `git reset --hard`.

Real working-tree reset/merge execution remains a daemon-owned staged implementation area, so the authored built-in subtask catalog now prefers safe inspection-oriented CLI surfaces over destructive placeholder commands.

## Deferred

- compiler support for direct `subtask_ref` style reuse from task YAML
- deduplicating inline task subtasks against standalone subtask files automatically
- richer authored prompt assets for every standalone subtask intent; that moves into the next prompt-pack authoring slice
