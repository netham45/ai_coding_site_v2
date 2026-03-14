# Route 02: Feature Delivery Ladder

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_feature_delivery_real.py`

## Goal

Prove feature-delivery decomposition from `epic.feature` through discovery, implementation, documentation, and E2E descendants.

## Main Path

- start `epic.feature`
- materialize descendants through phase, plan, and task tiers
- inspect selected descendant profiles and obligations

## Required Assertions

- `discovery`, `implementation`, `documentation`, and `e2e` bands all exist
- documentation and E2E obligations remain structurally visible
- descendant profile mapping is inspectable through runtime surfaces
- documentation, review, and E2E findings can route back into bounded remediation plus reverification work rather than ending as a terminal failed-verification leaf

## Adversarial Checks

- block parent completion before required bands exist
- reject parent-owned absorption of descendant implementation at merge time
- enforce remediation-turn caps and escalate when a corrective loop cannot close inside the current feature boundary

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Full feature-delivery decomposition with explicit docs and real-E2E obligations plus deterministic corrective loops after failed verification.
