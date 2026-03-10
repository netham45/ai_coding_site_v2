# YAML Inventory V2 Plan

## Purpose

This document defines the complete YAML artifact inventory that the system needs in order to move from high-level architecture into concrete spec-driven design.

The goal is to answer:

- what YAML families exist
- what each YAML family is for
- which YAMLs are canonical system definitions versus project-local overrides
- which YAMLs must compile into immutable workflow snapshots
- which YAMLs are still missing and need to be authored

This is not the final schema spec itself. It is the inventory and planning document for the full YAML surface.

Related documents:

- `notes/archive/superseded/yaml_schemas_spec_revised.md`
- `notes/planning/expansion/full_spec_expansion_plan.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`

---

## Goals Of This Inventory

This inventory should:

- enumerate every YAML family the system requires
- distinguish schema families from instance files
- distinguish built-in system YAML from project-local YAML
- identify which YAML files contribute directly to compiled workflows
- identify missing YAML families that are currently only implied
- provide a path toward `yaml_schemas_spec_v2.md`

---

## Core YAML Design Rules

The YAML layer should follow these rules.

### Rule 1: Schema validation is mandatory

No generated or edited YAML should be trusted without validation against an explicit schema family.

### Rule 2: Runtime executes compiled artifacts, not mutable YAML

Mutable YAML definitions are source inputs. Execution must run from compiled immutable workflow snapshots.

### Rule 3: Built-in and project-local YAML must be separable

The system should clearly distinguish:

- built-in system definitions
- project-local overrides
- project-local extensions

### Rule 4: Canonical generic forms should exist

Even if convenience aliases such as `phases`, `plans`, or `tasks` exist, the canonical YAML model should remain generic enough to support custom ladders and kinds.

### Rule 5: Every important behavior needs YAML ownership or an explicit code-only exception

If a behavior is intended to be configurable, policy-driven, or project-extensible, it should have a YAML home.

---

## YAML Families

The following are the major YAML families the system should support.

### Y01. Node definition YAML

Defines a node kind, its policies, entry task, prompts, available tasks, child constraints, and lifecycle behavior.

### Y02. Task definition YAML

Defines a named task phase for one or more node kinds and the subtasks that belong to it.

### Y03. Subtask definition YAML

Defines a reusable executable subtask structure or an inline subtask instance shape.

Current rendering note:

- subtask definitions may now include an optional `render_context` block for compile-time prompt/command substitution
- the current implementation intentionally limits renderable subtask fields to `prompt`, `command`, and `pause_summary_prompt`

### Y04. Validation check YAML

Defines validation checks such as file checks, schema checks, command exit codes, AI status checks, and content checks.

### Y05. Output definition YAML

Defines expected outputs that a subtask may be required to produce or register.

### Y06. Layout definition YAML

Defines child-node creation layouts including child kinds, goals, rationale, dependencies, acceptance criteria, and ordering hints.

### Y07. Hook definition YAML

Defines lifecycle hook insertions, applicability conditions, and hook actions.

### Y08. Override definition YAML

Defines project-local override behavior applied on top of built-in definitions.

### Y09. Project policy YAML

Defines project-level defaults, policies, gating behavior, auto-run behavior, merge behavior, testing requirements, and other cross-cutting settings.

### Y10. Review definition YAML

Defines review policies, review prompts, review scopes, review criteria, and review output structure.

### Y11. Testing definition YAML

Defines testing policies, test phases, test commands/checks, and test gate rules.

### Y12. Documentation definition YAML

Defines documentation generation policies, scopes, build triggers, and documentation output targets.

### Y13. Provenance extraction YAML

Defines policies or scopes for code-entity extraction, relation extraction, rationale attachment, and provenance refresh behavior.

### Y14. Rectification/rebuild definition YAML

Defines rebuild/rectify task structures, reset-from-seed policies, merge ordering policies, and upstream rebuild behaviors where configurable.

Implementation note:

- validation, review, testing, documentation, and rectification families are now backed by explicit rigid Pydantic models in the current implementation, with invalid field combinations rejected during YAML validation instead of being deferred to runtime consumers

### Y15. Session/runtime policy YAML

Defines runtime/session policies such as heartbeat intervals, idle thresholds, pause behavior, child session policies, and recovery rules.

Implementation note:

- runtime and runtime-policy YAML are now validated as rigid families in the current implementation, including catalog-backed checks for referenced subtask and higher-order YAML assets

### Y16. Environment/isolation policy YAML

Defines optional container/namespace isolation behavior for certain child work.

### Y17. CLI presentation YAML or command metadata YAML

Optional family if command groups, visibility, or output presets are intended to be configured declaratively.

### Y18. Action automation mapping YAML

Optional family if UI-visible actions are to be driven declaratively into CLI/runtime mutation paths.

---

## Canonical Family Classification

The following classification should be used during spec work.

| Family ID | Family | Category | Required | Compiles Into Workflow |
| --- | --- | --- | --- | --- |
| Y01 | Node definition | core runtime | yes | yes |
| Y02 | Task definition | core runtime | yes | yes |
| Y03 | Subtask definition | core runtime | yes | yes |
| Y04 | Validation check | core runtime | yes | yes |
| Y05 | Output definition | core runtime | yes | yes |
| Y06 | Layout definition | planning/runtime | yes | yes |
| Y07 | Hook definition | lifecycle/runtime | yes | yes |
| Y08 | Override definition | config system | yes | yes |
| Y09 | Project policy | config system | yes | maybe |
| Y10 | Review definition | quality gate | likely yes | yes |
| Y11 | Testing definition | quality gate | likely yes | yes |
| Y12 | Documentation definition | support system | likely yes | yes |
| Y13 | Provenance extraction | support system | maybe | maybe |
| Y14 | Rectification/rebuild definition | runtime/git | likely yes | yes |
| Y15 | Session/runtime policy | runtime policy | maybe | maybe |
| Y16 | Environment/isolation policy | runtime policy | maybe | maybe |
| Y17 | CLI command metadata | support system | optional | no |
| Y18 | Action automation mapping | support system | optional | no |

---

## Built-In vs Project-Local YAML

The YAML ecosystem should distinguish between built-in definitions and project-local files.

### Built-in system YAML

These define the default behavior of the orchestration system itself.

Examples:

- core node kinds
- core tasks
- core subtask types
- default validation rules
- default hook definitions
- default rebuild tasks

### Project-local extension YAML

These define project-specific additions that do not merely override built-ins.

Examples:

- project-defined node kinds
- project-defined tasks
- project-specific hooks
- project-specific quality gates
- project-specific docs generation rules

### Project-local override YAML

These modify the behavior of existing built-in or project-defined YAML.

Examples:

- changing node policies
- inserting new checks
- adjusting retry limits
- disabling auto-merge
- changing review or testing requirements

---

## Recommended YAML Directory Families

The exact directory structure can still be revised, but the inventory should assume families similar to the following.

```text
.ai/
  policies/
  overrides/
    nodes/
    tasks/
    layouts/
    hooks/
    reviews/
    testing/
    docs/
    runtime/
  nodes/
  tasks/
  subtasks/
  layouts/
  hooks/
  validations/
  reviews/
  testing/
  docs/
  provenance/
  rectification/
  runtime/
  environments/
```

Built-in system definitions could live in an internal package path with the same family breakdown.

---

## Required YAML Artifact Inventory

This section lists the concrete file groups that likely need to exist for a minimally complete default system.

## 1. Core node definition files

At minimum, the default ladder likely needs built-in node definition YAMLs for:

- top-level root node kind
- epic-like node kind
- phase-like node kind
- plan-like node kind
- task-like node kind

If the design wants generic defaults rather than semantic defaults, that may instead become:

- tier-0 generic node
- tier-1 generic node
- tier-2 generic node
- tier-3 generic node

Open decision:

- whether the default package should be semantic (`epic`, `phase`, `plan`, `task`) or generic (`tierN` with aliases)

Implementation note:

- the current built-in package uses semantic defaults (`epic`, `phase`, `plan`, `task`) while keeping the underlying hierarchy model generic in `kind` and `tier`

## 2. Core task definition files

The default system likely needs concrete task definition files for flows such as:

- initial research
- planning/decomposition
- child layout generation
- child review
- wait for dependencies
- run child nodes
- reconcile after child completion
- validation
- review
- testing
- docs generation
- finalization
- rectification from seed
- upstream rectification
- failure summarization
- pause-for-user summary

## 3. Core subtask definition files or templates

The default system likely needs reusable subtask definitions or canonical inline shapes for:

- run prompt
- run command
- build context
- validate
- review
- wait for children
- wait for sibling dependency
- spawn child session
- spawn child node
- reset to seed
- merge children
- write summary
- finalize node
- build docs
- update provenance
- run testing
- pause on user flag

## 4. Layout definition files

The system likely needs concrete layout YAML examples or defaults for:

- initial top-node decomposition
- phase creation from epic-like nodes
- plan creation from phase-like nodes
- task child creation from plan-like nodes
- manual layout definitions
- recovery or replanning layouts if supported

## 5. Hook definition files

The system likely needs hook YAML files for:

- validation insertion
- review insertion
- testing insertion
- docs insertion
- provenance refresh
- merge conflict handling hooks
- project-specific lifecycle hooks

## 6. Validation definition files

The system likely needs reusable validation YAML families for:

- file existence
- file updated
- command exit code
- JSON schema match
- YAML schema match
- AI JSON status
- content contains
- git state expectations
- branch state expectations
- summary registration expectations

## 7. Review definition files

The system likely needs review YAML files for:

- parent requirement review
- child-layout review
- reconcile review
- pre-finalization review
- merge review
- docs quality review
- policy compliance review

## 8. Testing definition files

The system likely needs testing YAML files for:

- unit test gates
- integration test gates
- project-defined test suites
- smoke checks
- test retry policies
- test failure summary policies

## 9. Documentation definition files

The system likely needs docs YAML files for:

- local node docs build
- merged tree docs build
- static analysis extraction scope
- rationale/provenance integration
- docs output targets

## 10. Provenance extraction files

The system may need YAML for:

- entity extraction policy
- relation extraction policy
- rationale attachment rules
- refresh cadence during rebuild/finalize

## 11. Rectification/rebuild files

The system likely needs concrete YAML for:

- regenerate subtree task
- rectify from seed task
- merge child finals task
- conflict reconcile task
- upstream rectify task
- rebuild review task
- rebuild docs task

## 12. Runtime/session policy files

The system may need YAML for:

- heartbeat interval
- idle timeout
- nudge policy
- session recovery policy
- child session limits
- retry thresholds

## 13. Environment/isolation files

The system may need YAML for:

- isolated environment requirements
- allowed runtime profiles
- container image/preset selection
- namespace or network isolation policy

---

## Canonical Compilation Inputs

The following YAML families likely contribute directly to compiled workflow snapshots and should therefore preserve full source lineage:

- node definitions
- task definitions
- subtask definitions
- layouts
- hooks
- overrides
- review definitions
- testing definitions
- documentation definitions
- rectification definitions
- project policy files that alter workflow behavior

Open question:

- whether runtime/session policy YAML should compile into workflow snapshots or remain external runtime policy

---

## YAML Families That Need Sharper Specification

Based on the current docs, the following YAML families still need the most work.

### 1. Review definition YAML

Review exists as a concept and as a subtask type, but not yet as a fully inventoried YAML family.

### 2. Testing definition YAML

Testing is clearly a desired capability, but its YAML surface is not yet concretized.

### 3. Documentation definition YAML

Docs generation exists conceptually, but the config family is not yet clearly defined.

### 4. Provenance extraction YAML

Provenance tables exist, but the policy/config layer is not yet well defined.

### 5. Runtime/session policy YAML

The runtime model exists, but declarative policy surfaces for heartbeat, nudge, or child session behavior are still unclear.

### 6. Environment/isolation policy YAML

This remains mostly conceptual and needs a decision on whether it belongs in YAML, code, or both.

### 7. Action automation mapping YAML

This may or may not belong in YAML, but the action-to-automation mapping itself must exist somewhere.

---

## Open Design Decisions

The following decisions need to be made during YAML v2 work.

### D01. Semantic defaults vs generic defaults

Should built-in defaults be explicitly `epic`, `phase`, `plan`, `task`, or should the built-ins be generic tier models with semantic aliases layered on top?

### D02. Inline subtasks vs reusable subtask files

Should subtasks mostly exist inline within task definitions, or should there be reusable named subtask documents referenced by task YAML?

### D03. Review/testing/docs as families vs hook-driven task insertions

Should review/testing/docs be their own YAML families, or should they only be hook-driven compositions of more generic tasks/subtasks?

### D04. Runtime policy compile boundary

Which runtime policies compile into immutable workflow snapshots versus remaining runtime-environment settings?

### D05. Environment policy placement

Should environment/isolation rules live in YAML, infrastructure config, or a mixed model?

### D06. Provenance config depth

How much of provenance extraction should be declarative versus code-defined?

---

## Recommended Next YAML Follow-On Documents

The next YAML-focused docs to create are:

- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`

If provenance and environment policies become large enough, add:

- `notes/provenance_yaml_plan.md`
- `notes/runtime_environment_policy_plan.md`

---

## Initial Coverage Assessment By Family

| Family ID | Family | Current Coverage | Notes |
| --- | --- | --- | --- |
| Y01 | Node definition | partially covered | Strong concept, but not fully concretized into full field inventory and default files. |
| Y02 | Task definition | partially covered | Core structure exists, but full default task catalog is missing. |
| Y03 | Subtask definition | partially covered | Core shape exists, but reusable library strategy is undecided. |
| Y04 | Validation check | partially covered | Core check types exist, but result model and broader examples are missing. |
| Y05 | Output definition | partially covered | Basic structure exists, but output taxonomy likely needs expansion. |
| Y06 | Layout definition | partially covered | Core layout shape exists, but full default layout library is missing. |
| Y07 | Hook definition | partially covered | Hook points exist, but ordering/composition rules need more detail. |
| Y08 | Override definition | partially covered | Resolution order exists, but override file shapes and examples need work. |
| Y09 | Project policy | missing | Strong need implied, but not yet concretely inventoried. |
| Y10 | Review definition | missing | Review exists conceptually, but not yet as a proper YAML family. |
| Y11 | Testing definition | missing | Testing needs dedicated YAML inventory and rules. |
| Y12 | Documentation definition | missing | Docs generation config surface needs definition. |
| Y13 | Provenance extraction | missing | Provenance config layer remains unclear. |
| Y14 | Rectification/rebuild definition | partially covered | Example exists, but full library is missing. |
| Y15 | Session/runtime policy | missing | Runtime policy YAML still needs explicit design. |
| Y16 | Environment/isolation policy | missing | Environment config remains conceptual. |
| Y17 | CLI command metadata | missing | Optional; not yet decided. |
| Y18 | Action automation mapping | missing | Strong need, but artifact form undecided. |

---

## Exit Criteria For YAML Inventory Completion

This inventory phase should be considered complete when:

- every YAML family has been classified as required, optional, or explicitly rejected
- every required YAML family has a clear purpose and ownership
- every built-in default file set is enumerated
- the compile boundary is clear for workflow-affecting YAML
- missing families are listed explicitly for v2 work

At that point, the YAML system is concrete enough to move into the actual v2 schema writing pass.
