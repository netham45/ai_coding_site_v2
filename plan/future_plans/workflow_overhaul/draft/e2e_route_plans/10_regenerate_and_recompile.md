# Route 10: Regenerate And Recompile

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_regenerate_and_recompile_real.py`

## Goal

Prove that regenerate, rectify, and recompile preserve selected-profile constraints and update derived obligations honestly.

## Main Path

- create a profiled node
- regenerate or rectify after changes
- inspect the recompiled workflow state

## Required Assertions

- selected profile remains visible across versions where intended
- recompile updates effective layout, child-role mapping, and blocked-step metadata honestly
- stale compiled obligations are not silently reused

## Adversarial Checks

- recompile after descendant-affecting changes
- inspect changed blocked metadata and role obligations

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Profile-aware recompile and rectify correctness.
