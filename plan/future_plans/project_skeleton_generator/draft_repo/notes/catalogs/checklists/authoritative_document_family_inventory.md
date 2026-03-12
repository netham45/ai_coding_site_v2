# Authoritative Document Family Inventory

## Purpose

Identify which document families are treated as authoritative implementation assets.

## Starter Families

| Family | Why it matters | Expected test coverage |
| --- | --- | --- |
| lifecycle notes | govern stage-specific behavior | document-structure checks |
| task plans | govern meaningful work | plan-schema checks |
| development logs | reconstruct work and proof | log-schema checks |
| operational-state checklist | records maturity truthfully | checklist-structure checks |
| feature checklists | track implementation and proof status | checklist-schema checks |
| verification command catalog | defines canonical proving commands | doc-consistency checks |
| flow inventory | tracks relevant flows and E2E mapping | mapping and schema checks |

## Rule

If a new document family becomes authoritative, add it here and add or update the relevant consistency tests in the same change.
