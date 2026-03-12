# Route 03: Review And Remediation Ladder

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_review_remediation_real.py`

## Goal

Prove review, remediation, and re-review as separate descendants rather than one collapsed stream.

## Main Path

- start `epic.review`
- materialize review-focused descendants
- drive review, remediation, and re-review through runtime-visible surfaces

## Required Assertions

- review and remediation remain structurally distinct
- remediation is traceable back to findings
- re-review depends on remediation output

## Adversarial Checks

- block closure when remediation is missing
- block re-review closure when remediation proof is missing

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Traceable review-to-remediation-to-re-review lifecycle.
