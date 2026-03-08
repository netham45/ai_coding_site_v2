# Review, Testing, And Docs YAML Plan

## Purpose

This document defines how review, testing, and documentation should be treated in the YAML/configuration layer.

These three areas are currently present in the design, but they are not yet fully settled as first-class artifact families with consistent behavior across:

- YAML
- database persistence
- runtime pseudocode
- CLI surfaces
- auditability

The goal of this document is to close that gap enough to support the v2 spec rewrite.

Related documents:

- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Problem

Review, testing, and docs are currently in an awkward middle state:

- they are clearly important
- they appear in multiple specs
- they influence completion/finalization behavior
- they likely need CLI visibility
- they likely need durable persistence

But they are not yet fully frozen as:

- first-class YAML families
- explicit result models
- explicit runtime stages
- explicit built-in file sets

This document proposes the shape needed to make them concrete.

---

## Recommended Decision

Review, testing, and docs should be treated as first-class configurable families.

They may still be inserted via hooks or selected by policy, but they should not remain only implicit generic subtasks.

Recommended stance:

- review is a first-class family
- testing is a first-class family
- docs is a first-class family

Hooks may still inject them, but the injected content should point to concrete review/testing/docs definitions rather than inventing structure ad hoc.

---

## Why These Should Be First-Class Families

### Review

Review has:

- inputs
- criteria
- scope
- outputs
- pass/fail/revise consequences

That is too rich to leave as only an unstructured prompt or inline generic subtask.

### Testing

Testing has:

- suite identity
- commands/checks
- retry behavior
- result persistence
- gating consequences

That is too rich to treat as only an ordinary validation check.

### Docs

Docs generation has:

- multiple scopes
- multiple input sources
- output artifacts
- rebuild triggers
- downstream users

That is too rich to leave as only a simple command step.

---

## Proposed YAML Families

The following YAML families should be formally added or solidified.

## RTD01. Review definition YAML

Purpose:

- define review scopes
- define criteria
- define input sources
- define prompts or review instructions
- define pass/fail/revise outcomes
- define persistence expectations

### Proposed conceptual shape

```yaml
review_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    task_ids:
      - string
    lifecycle_points:
      - string
  scope: layout|node_output|merge_result|docs|policy_compliance|custom
  description: string
  inputs:
    include_parent_requirements: boolean
    include_child_summaries: boolean
    include_acceptance_criteria: boolean
    include_changed_files: boolean
    include_validation_results: boolean
    include_test_results: boolean
  prompt: string
  criteria:
    - string
  on_result:
    pass_action: continue
    revise_action: rerun_subtask|rerun_task|pause_for_user
    fail_action: fail_to_parent|pause_for_user
```

## RTD02. Testing definition YAML

Purpose:

- define test suites and commands
- define test scope and gating level
- define retries and failure summaries
- define pass/fail thresholds

### Proposed conceptual shape

```yaml
testing_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    task_ids:
      - string
    lifecycle_points:
      - string
  scope: unit|integration|smoke|project_custom
  description: string
  commands:
    - command: string
      working_directory: string
      env:
        KEY: value
  retry_policy:
    max_attempts: integer
    rerun_failed_only: boolean
  pass_rules:
    require_exit_code_zero: boolean
    max_failed_tests: integer
  on_result:
    pass_action: continue
    fail_action: fail_to_parent|pause_for_user|allow_override
```

## RTD03. Documentation definition YAML

Purpose:

- define doc scopes and build triggers
- define input sources
- define output targets
- define local vs merged views

### Proposed conceptual shape

```yaml
documentation_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    lifecycle_points:
      - string
  scope: local|merged|entity_history|rationale_view|custom
  description: string
  inputs:
    include_static_analysis: boolean
    include_entity_relations: boolean
    include_node_summaries: boolean
    include_prompt_history: boolean
    include_review_results: boolean
    include_test_results: boolean
  outputs:
    - path: string
      format: markdown|html|json|yaml
  rebuild_policy:
    on_finalize: boolean
    on_rectify: boolean
    on_docs_request: boolean
```

---

## Relationship To Hooks

Review, testing, and docs should integrate with hooks like this:

### Recommended model

1. review/testing/docs definitions are first-class reusable YAML documents
2. hook definitions may insert references to those documents
3. task definitions may also explicitly reference those documents
4. compilation resolves all of the above into concrete compiled stages

This avoids two bad outcomes:

- ad hoc inline review/testing/docs logic everywhere
- duplicated semantics between tasks and hooks

---

## Relationship To Generic Subtasks

Review, testing, and docs should still use subtask execution under the hood.

Recommended layering:

1. review/testing/docs definitions describe the semantic stage
2. compilation converts them into concrete subtasks or task sections
3. runtime executes concrete compiled stages

This means:

- they are not “special” in execution mechanics
- they are “special” in configuration and persistence semantics
- their default prompts should still be authored centrally rather than improvised at runtime

---

## Default Prompt Templates

This note should carry concrete default prompt examples for the three first-class families.

The broader prompt pack lives in `notes/specs/prompts/prompt_library_plan.md`, but these templates belong here because they define family-level expectations.

## Review prompt template

```text
Review the current stage output for node <node_id>.

Scope:
<review_scope>

Requirements and criteria:
<criteria>

Inputs available:
- changed files
- acceptance criteria
- validation results
- test results if present
- child summaries if present

Return JSON only:
{
  "status":"PASS"|"REVISE"|"FAIL",
  "summary":"<concise review assessment>",
  "findings":["..."]
}
```

## Testing prompt template

This should be used when a testing stage needs an AI-visible instruction layer in addition to raw test commands.

```text
Evaluate the testing stage for node <node_id>.

Commands already run:
<commands_run>

Observed outputs:
<command_outputs>

Pass rules:
<pass_rules>

Return JSON only:
{
  "status":"PASS"|"FAIL",
  "summary":"<concise test assessment>",
  "failed_commands":["..."]
}
```

## Docs prompt template

```text
Build the documentation outputs for node <node_id>.

Documentation scope:
<doc_scope>

Include:
- node goal and rationale
- output artifacts or merged outputs
- relevant summaries
- review and test outcomes when available
- prompt lineage where useful

Write outputs to:
<output_paths>

Return JSON only:
{
  "status":"OK",
  "outputs":["..."],
  "summary":"<what was documented>"
}
or
{"status":"FAIL","message":"<reason>"}
```

---

## Built-In YAML Library Additions

The built-in library should include concrete files for these families.

## Review built-ins

### Required

- `reviews/layout_against_prompt.yaml`
- `reviews/node_against_requirements.yaml`
- `reviews/reconcile_output.yaml`
- `reviews/pre_finalize.yaml`

### Strongly recommended

- `reviews/merge_result_review.yaml`
- `reviews/docs_quality_review.yaml`
- `reviews/policy_compliance_review.yaml`

## Testing built-ins

### Required

- `testing/default_unit_test_gate.yaml`
- `testing/default_integration_test_gate.yaml`
- `testing/default_smoke_test_gate.yaml`

### Strongly recommended

- `testing/test_retry_policy.yaml`
- `testing/test_failure_summary.yaml`
- `testing/project_command_suite.yaml`

## Docs built-ins

### Required

- `docs/build_local_node_docs.yaml`
- `docs/build_merged_tree_docs.yaml`
- `docs/default_doc_views.yaml`

### Strongly recommended

- `docs/static_analysis_scope.yaml`
- `docs/rationale_merge_rules.yaml`
- `docs/entity_history_view.yaml`

---

## Proposed Runtime Treatment

The runtime should treat these families as explicit stages with explicit result persistence.

## Review runtime treatment

Review stages should:

- build structured review input context
- execute review logic
- produce structured review output
- decide pass/revise/fail/pause behavior

## Testing runtime treatment

Testing stages should:

- discover or load configured test suites
- execute test commands
- normalize results
- apply retry logic
- determine pass/fail/override behavior

## Docs runtime treatment

Docs stages should:

- gather configured inputs
- build the requested doc scopes
- persist built artifacts
- register build metadata

---

## Proposed Database Treatment

The DB should likely add explicit result structures for review and testing, and maybe richer structures for docs.

## Review result persistence

Recommended addition:

- `review_results`

Possible fields:

- `id`
- `node_version_id`
- `node_run_id`
- `compiled_subtask_id`
- `review_definition_id`
- `scope`
- `status`
- `criteria_json`
- `findings_json`
- `summary`
- `created_at`

## Testing result persistence

Recommended addition:

- `test_results`

Possible fields:

- `id`
- `node_version_id`
- `node_run_id`
- `compiled_subtask_id`
- `testing_definition_id`
- `suite_name`
- `status`
- `attempt_number`
- `results_json`
- `summary`
- `created_at`

## Docs result persistence

Current `node_docs` may be sufficient for artifact storage, but additional build metadata may still be useful.

Possible addition if needed:

- `doc_build_results`

Potential purpose:

- record each docs build event
- capture inputs and generator metadata
- capture success/failure state

Open question:

- whether `node_docs` plus summaries is enough, or whether build-event history deserves a separate table

---

## Proposed CLI Treatment

The CLI should expose all three families explicitly.

## Review CLI

Likely needed:

- `ai-tool review show --node <id>`
- `ai-tool review show --run <id>`
- `ai-tool review run --node <id> --scope <scope>`
- `ai-tool review results --node <id>`

## Testing CLI

Likely needed:

- `ai-tool testing show --node <id>`
- `ai-tool testing show --run <id>`
- `ai-tool testing run --node <id>`
- `ai-tool testing results --node <id>`

## Docs CLI

Already partially present, but likely needs stronger formalization:

- `ai-tool docs build-node-view --node <id>`
- `ai-tool docs build-tree --node <id>`
- `ai-tool docs list --node <id>`
- `ai-tool docs show --node <id> --scope <scope>`
- maybe `ai-tool docs results --node <id>`

---

## Recommended Canonical Ordering

One of the biggest unresolved questions is where review, testing, and docs sit relative to validation, provenance, and finalization.

Recommended canonical default ordering:

1. reconcile node-local output
2. validation
3. review
4. testing
5. provenance update
6. docs build
7. finalize node

### Why this order

Validation should run before review so obviously invalid output does not waste review effort.

Review should run before testing because review may reject the output structurally or semantically before heavier testing runs.

Testing should run before provenance/docs final build because failed test gates should generally block final artifact generation.

Provenance should run before docs so docs can consume updated entity/rationale information.

Docs should run before finalization so final node state includes the generated documentation outputs.

### Open question

- whether some projects should allow testing before review for cost or speed reasons

Recommended answer:

- support override capability, but freeze the above as the built-in default order

---

## Built-In Task Integration Model

The default task library should integrate these families in one canonical way.

Recommended model:

- `validate_node` references validation definitions
- `review_node` references review definitions
- `test_node` references testing definitions
- `build_node_docs` references documentation definitions
- `update_provenance` remains a sibling support task

This creates a simple default task chain while still allowing hooks to insert or modify stages.

---

## Key Open Decisions

### D01. Review revision behavior

When review fails, should the default behavior be:

- rerun local reconcile
- rerun prior task
- pause for user
- fail to parent

Recommended default:

- revise locally once if configured, then pause or fail according to node policy

### D02. Testing failure overrides

Should a user be able to approve continuation past a failed test gate?

Recommended default:

- only if explicitly enabled by project policy

### D03. Docs on failed quality gates

Should docs build if review or testing fails?

Recommended default:

- no, unless building a failure-report artifact is explicitly configured

### D04. Docs event table

Does docs generation need a separate build-event table, or is `node_docs` enough?

Recommended tentative answer:

- likely add build-event history if docs become operationally important

---

## Highest-Priority Gaps This Plan Addresses

This document is intended to help close:

- GAP-001 review/testing/docs modeling
- GAP-004 quality-gate ordering
- GAP-007 testing persistence model
- GAP-008 review persistence model
- part of GAP-025 docs/provenance ordering

---

## Recommended Next Follow-On Work

The next useful work after this document is:

1. fold these families into the future `yaml_schemas_spec_v2.md`
2. add review/test result structures to the future `database_schema_spec_v2.md`
3. update the future runtime and lifecycle v2 specs with canonical ordering
4. rerun `notes/catalogs/traceability/cross_spec_gap_matrix.md` and lower the status of the gaps this resolves

---

## Exit Criteria

This planning document is complete enough when:

- review/testing/docs are clearly treated as first-class families
- their YAML purpose is defined
- their likely DB result models are identified
- their runtime roles are clear
- their CLI surfaces are explicit
- their default ordering is frozen well enough for v2 rewrite

At that point, one of the biggest cross-spec holes is small enough to fold into the canonical v2 specs.
