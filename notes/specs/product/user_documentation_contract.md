# User Documentation Contract

## Purpose

Define the authoritative boundary and maintenance rules for user-facing and operator-facing documentation in the live repository.

## Documentation Audiences

At minimum, account for:

- contributors bootstrapping the repository locally
- operators using the CLI or website UI to inspect and control runtime work
- readers looking for supported command, configuration, and environment references
- operators following recovery or troubleshooting procedures

## Authoritative Boundaries

- `docs/` is the primary user-facing and operator-facing documentation tree
- `notes/` remains the governance, planning, specification, and traceability tree
- `notes/scenarios/` is a historical analysis and migration-pointer surface by default; files there are not authoritative user/operator docs unless explicitly promoted again
- YAML `docs` assets define machine-readable docs-generation inputs and outputs; they do not replace the human-facing documentation tree

## Required Documentation Triggers

Documentation review is required when work changes:

- user-visible or operator-visible behavior
- setup or bootstrap steps
- supported commands, flags, or examples
- configuration or environment requirements
- supported workflows
- troubleshooting or recovery procedures
- limitations, prerequisites, or support boundaries

## Required Plan And Checklist Linkage

Task plans created or materially revised on or after 2026-03-13 must include:

- `## Documentation Impact`
- `## Documentation Verification`

Those sections must record one of:

- documentation update required
- documentation reviewed with no change required
- documentation not applicable

Feature checklists must track:

- user documentation status
- documentation surfaces affected
- notes status separately from user documentation status

Relevant flow-traceability entries must track:

- whether documentation is required for the flow
- which documentation surfaces are affected

## Documentation Invariants

- user-facing docs must not claim unsupported behavior
- operator docs and runbooks must not describe recovery steps the runtime does not actually support
- reference docs must not drift from supported commands, config, or interfaces
- plans and checklists must not leave documentation impact implicit when the change is user-visible or operator-visible

## Proof Surface

- Bounded proof: `PYTHONPATH=src python3 -m pytest tests/unit/test_user_documentation_governance_docs.py -q`
- Supporting structured-flow proof: `PYTHONPATH=src python3 -m pytest tests/unit/test_relevant_user_flow_inventory.py -q`
