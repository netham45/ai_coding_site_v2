# Feature Checklists

This directory contains the canonical implementation-status surface for tracked features.

Use these files together:

- `feature_checklist_standard.md`: checklist rules, allowed statuses, template, and canonical DU-01 verification command
- `feature_checklist_backfill.md`: current backfilled status entries for the existing feature-plan set
- `verification_command_catalog.md`: canonical verification command families for bounded, integration, flow, performance, and current real-E2E proof
- `notes/catalogs/checklists/e2e_execution_policy.md`: local, CI, gated/manual, and release-readiness execution policy for the current proving ladder
- `authoritative_document_family_inventory.md`: inventory of authoritative document families and their schema/testing strategies
- `document_schema_rulebook.md`: current rigidity rules for authoritative document families
- `document_schema_test_policy.md`: canonical command and adoption policy for document-schema tests

Boundary:

- `notes/catalogs/inventory/major_feature_inventory.md` is the architecture inventory and design-maturity surface
- `notes/catalogs/checklists/*.md` is the implementation and verification status surface

When feature plans, E2E targets, or proving status change, update the backfill in the same change.
