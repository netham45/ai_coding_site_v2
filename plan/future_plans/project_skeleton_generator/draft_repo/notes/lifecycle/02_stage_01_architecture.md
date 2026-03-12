# Stage 01: Architecture

## Purpose

Architecture converts the initial concept into explicit system boundaries, durable state expectations, runtime authority rules, and first proving commands.

## Required Outcomes

- primary boundaries are documented
- chosen stack decisions are confirmed or revised explicitly
- code-vs-config lines are explicit
- initial invariants are expanded beyond rough notes
- first canonical verification command catalog exists
- document-family expectations are named

## Required Artifacts

- `notes/specs/architecture/code_vs_config_delineation.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/architecture/stack_decision_record.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`

## Common Failure Modes

- using implementation convenience as architecture
- letting the starter repo imply a language or framework choice that genesis never actually decided
- letting config assets absorb runtime authority
- adding commands without documenting them
- claiming setup readiness before boundary notes exist

## Exit Condition

This stage is complete enough to exit when setup work can begin without contributors having to guess where authority, durability, and policy belong.
