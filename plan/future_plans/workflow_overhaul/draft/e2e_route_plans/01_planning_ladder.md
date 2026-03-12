# Route 01: Planning Ladder

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_planning_ladder_real.py`

## Goal

Prove the planning-oriented decomposition ladder from `epic.planning` down to planning-oriented descendants.

## Main Path

- start `epic.planning`
- inspect `workflow brief`, `node types`, and `node profiles`
- materialize phase, plan, and task descendants
- inspect selected lower-tier profiles

## Required Assertions

- planning roles exist at each tier
- planning-oriented child-profile mapping is preserved in compiled state
- recommended planning descendants are runtime-visible

## Adversarial Checks

- block completion before required planning children exist
- block merge before planning descendants finish where required

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Profile-aware planning decomposition that does not collapse into implementation-first defaults.
