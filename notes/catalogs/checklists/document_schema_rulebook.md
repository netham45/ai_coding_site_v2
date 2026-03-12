# Document Schema Rulebook

## Purpose

This note defines the current schema and rigidity rules for authoritative document families.

It is the implementation surface for DS-02, DS-03, and DS-04.

## Family Rules

### Plan And Checklist Families

Applies to:

- `plan/web/setup/*.md`
- `plan/features/*.md`
- `plan/web/features/*.md`
- `plan/tasks/*.md`
- `plan/checklists/*.md`
- `plan/update_tests/*.md`
- `plan/e2e_tests/*.md`
- `plan/web/verification/*.md`
- `plan/doc_updates/*.md`
- `plan/doc_schemas/*.md`

Required rules:

- setup plans must include:
  - `## Goal`
  - `## Scope`
  - `## Exit Criteria`
- standard richer plan schema families must include:
  - `## Goal`
  - `## Rationale`
  - `## Related Features`
  - `## Required Notes`
  - `## Scope`
  - `- Rationale: ...`
  - `- Reason for existence: ...`
  - `Read these feature plans for implementation context and interaction boundaries:`
  - `Read these note files before implementing or revising this phase:`
  - explicit scope coverage for:
    - `Database:`
    - `CLI:`
    - `Daemon:`
    - `YAML:`
    - `Prompts:`
    - `Tests:`
    - `Performance:`
    - `Notes:`
- task plans must additionally include:
  - `## Verification`
  - `## Exit Criteria`
- verification checklists must include:
  - `## Goal`
  - `## Verify`
  - `## Tests`
  - `## Notes`
- explicit related-feature and required-note references where the family uses those sections
- current outputs and canonical verification command sections for `plan/doc_updates/*.md` and `plan/doc_schemas/*.md`
- checklist and release/readiness docs must point to:
  - `notes/catalogs/checklists/feature_checklist_standard.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`

### Feature Checklist Family

Applies to:

- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

Required rules:

- allowed status vocabulary only
- full feature-plan coverage
- explicit E2E target and E2E status fields
- explicit current-command linkage

### Flow, Traceability, And E2E Families

Applies to:

- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

Required rules:

- bounded-proof status and real-E2E completion must be distinguishable
- target-assignment docs must state when they do not claim completion
- simulation-derived docs must state when they are planning or bounded-proof only
- flow coverage must expose one flow-status summary table with:
  - bounded proof status
  - real E2E target
  - real E2E completion
- the structured relevant-user-flow inventory must:
  - declare its interpretation boundary relative to `flows/*.md`
  - include one entry per canonical relevant flow
  - record affected-system scope across the six required systems
  - record invariants, canonical commands, and proof statuses for each tracked flow
  - link every tracked flow to an existing canonical `flows/*.md` file

### Traceability Catalog Family

Applies to:

- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Required rules:

- coverage, gap, and planning statuses must be scoped explicitly so they are not mistaken for implementation completion or proving status
- traceability catalogs that use `covered`, `partially_covered`, `open`, `implementation_open`, or similar values must define what those values mean in-document
- traceability and gap docs must point readers to the checklist and command layers when implementation or proving status lives elsewhere

### Audit Checklist Family

Applies to:

- `notes/catalogs/audit/auditability_checklist.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`

Required rules:

- audit/review-only status values must be scoped explicitly so they are not mistaken for implementation completion claims
- implementation-facing audit checklists that are not the canonical proving surface must say where implementation and proving status live instead
- flow coverage must distinguish bounded proof from real-E2E completion

### Command And Execution Policy Families

Applies to:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `README.md`

Required rules:

- canonical commands live in the command catalog
- execution tiers live in the execution policy
- README and other authoritative docs link back to those canonical sources instead of inventing parallel command sets

### Operational Log Family

Applies to:

- `notes/logs/**/*.md`

Required rules:

- log files must live under a structured subdirectory such as `notes/logs/features/`, `notes/logs/doc_updates/`, or another explicitly named batch family
- each log file must include one or more entries
- each entry must record:
  - `Timestamp:`
  - `Task ID:`
  - `Task title:`
  - `Status:`
  - `Affected systems:`
  - `Summary:`
  - `Plans and notes consulted:`
  - `Commands and tests run:`
  - `Result:`
  - `Next step:`
- log status values must stay within the adopted vocabulary in `AGENTS.md`
- log entries must cite their governing task plan under `plan/tasks/`

## Enforcement Posture

- tests should enforce structure, linkage, status vocabulary, and command-policy references
- tests should not enforce brittle prose wording outside the explicitly declared schema fields
- exploratory and archived notes remain outside this rulebook unless promoted into an authoritative family
