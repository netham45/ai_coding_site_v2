# Operational State Extraction Strategy

## Goal

Describe how a future tool would extract this repository's operational framework without dragging product-specific implementation details into the target project.

## Extraction Model

The future implementation should treat repository doctrine as a structured catalog of reusable operational assets.

### Layer 1: Core doctrine sources

Primary files to read:

- `AGENTS.md`
- `plan/README.md`
- `plan/tasks/README.md`
- `plan/checklists/README.md`
- `plan/e2e_tests/README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

These are the main sources for:

- required artifact families
- document status rules
- verification posture
- plan and checklist doctrine
- task/log obligations
- lifecycle progression
- lifecycle sub-step expectations
- workflow profile direction

### Layer 2: Supporting doctrine sources

Supporting files to sample:

- `notes/catalogs/audit/*.md`
- `notes/catalogs/traceability/*.md`
- `notes/scenarios/**/*.md`
- `notes/specs/architecture/*.md`
- `notes/specs/prompts/*.md`
- `plan/setup/*.md`
- `plan/features/*.md`
- `plan/doc_updates/*.md`
- `plan/doc_schemas/*.md`
- `plan/e2e_tests/*.md`

These should be used to discover:

- recurring section patterns
- lifecycle sub-phases
- cross-system language
- checklist categories
- note families worth templating

### Layer 3: Example artifacts

The future implementation should inspect examples, not just doctrine files:

- sample task plans under `plan/tasks/`
- sample development logs under `notes/logs/`
- sample feature plans under `plan/features/`
- sample checklist docs under `plan/checklists/`

This lets the generator learn the actual artifact shape used in practice.

## Proposed Intermediate Representation

The extractor should normalize the source repository into a machine-friendly object such as:

```yaml
operational_profile:
  doctrine_version: draft_v1
  source_repo_name: ai_coding_site_v2
  required_directories:
    - code
    - notes
    - notes/logs
    - plan
    - plan/tasks
    - plan/checklists
    - simulations
    - tests/unit
    - tests/e2e
  core_systems:
    - database
    - cli
    - daemon
    - yaml
    - prompts
  lifecycle_stages:
    - genesis
    - architecture
    - setup
    - feature_planning
    - implementation
    - bounded_verification
    - e2e_verification
    - hardening
    - maintenance
    - evolution
  required_document_families:
    - agents
    - task_plans
    - development_logs
    - lifecycle_notes
    - operational_state_checklist
    - verification_commands
    - feature_checklists
  workflow_model:
    node_kinds: [epic, phase, plan, task]
    profile_families:
      epic: [planning, feature, review, documentation]
      phase: [genesis, architecture, setup, discovery, implementation, documentation, e2e, review, remediation]
      plan: [bootstrap, authoring, execution, verification, doc_alignment]
      task: [note_authoring, structure_bootstrap, implementation, docs, checklist_alignment, log_update, e2e]
  status_vocabularies:
    feature_statuses: [planned, in_progress, implemented, partial, verified, flow_complete, release_ready, blocked, deferred]
    system_statuses: [not_applicable, planned, in_progress, implemented, verified, partial, blocked, deferred]
    log_statuses: [started, in_progress, blocked, changed_plan, bounded_tests_passed, e2e_pending, e2e_passed, partial, deferred, complete]
  stage_governance:
    current_stage_source: plan/checklists/00_project_operational_state.md
    stage_notes_directory: notes/lifecycle
    stage_substeps_required: true
    agents_mode: concise_stage_governance
```

The generated project should come from this representation, not from ad hoc file copying.

## Extraction Passes

### Pass 1: Doctrine inventory

Collect:

- required doc families
- required section names
- status vocabularies
- canonical commands
- directory expectations
- reusable workflow-profile vocabulary

### Pass 2: Reusable template boundaries

Classify each source artifact into one of:

- reusable almost as-is
- reusable with token substitution
- reusable only as summarized doctrine
- source-repo-specific and not portable

Examples:

- `AGENTS.md`: reusable with parameter substitution
- feature inventory: source-repo-specific
- task-plan schema: reusable
- development-log schema: reusable
- current feature plans: not directly reusable
- lifecycle doctrine: reusable as summarized guidance

### Pass 3: Scaffold contract generation

Produce a generator-facing contract that answers:

- what folders must exist
- what seed docs must exist
- what placeholders each doc needs
- what command surfaces are seeded with placeholder commands
- what checklist rows start as planned versus not_applicable
- what the operational-state checklist must track
- which lifecycle stages map to which workflow profiles

### Pass 4: Target-project personalization

Ask for or receive:

- project name
- short mission statement
- chosen primary systems
- chosen stack defaults
- whether the repo wants exactly five systems or a configurable count
- desired strictness level for docs and checklists

### Pass 5: Template rendering

Render the target repository with:

- base folder tree
- seeded documents
- initial inventory notes
- placeholder tests
- starter plans and checklists
- starter operational-state checklist
- starter development log
- starter workflow-overhaul integration hints

## Extraction Heuristics

The future extractor should prefer explicit doctrine over implicit inference.

Priority order:

1. Explicit statements in `AGENTS.md`
2. Explicit statements in document-family notes
3. Explicit section and vocabulary patterns in tested docs
4. Repeated patterns in example artifacts
5. Code-based inference only where the doctrine is silent

This prevents the generator from inheriting accidental habits instead of actual policy.

Where the workflow-overhaul notes define a reusable profile concept, the extractor should preserve that as structured data rather than flattening it into prose-only lifecycle guidance.

Where the source repository keeps stage-specific detail outside `AGENTS.md`, the extractor should preserve that separation instead of re-inlining the rules into a generated `AGENTS.md`.

## Important Boundary

The future extractor should not try to reproduce the whole repo's current maturity.

Instead, it should extract:

- the framework for growing a disciplined repo

and avoid extracting:

- the full burden of a mature repo with dozens of active feature plans

That means the generated project should begin with a minimal but coherent subset of doctrine, then add stronger families later through its own lifecycle notes.
