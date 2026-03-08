# Action Automation Matrix

## Purpose

This document maps user-visible actions to their automation surfaces.

The goal is to ensure the system satisfies the original requirement that everything the user can do in the interface should also be automatable.

For each action, this matrix should answer:

- what the user-visible action is
- what CLI command or command family performs it
- what runtime component owns the action
- what durable database state changes
- what audit trail or history should exist afterward
- what gaps still exist

Authority assumption:

- the daemon/runtime owns live operational mutations
- the database records the durable consequences of those mutations
- the CLI reaches those actions through the daemon API rather than by directly coordinating through database writes

Related documents:

- `notes/original_concept.md`
- `notes/cli_surface_spec_revised.md`
- `notes/runtime_pseudocode_plan.md`
- `notes/cross_spec_gap_matrix.md`

---

## Scope

This matrix is focused on user-visible and operator-visible actions.

That includes:

- creating nodes
- editing plans and layouts
- starting runs
- pausing/resuming/canceling work
- reviewing state
- approving gated operations
- triggering rebuilds
- inspecting rationale and history
- attaching to sessions
- querying docs and provenance

This document is not yet a full permission model. It is a capability mapping artifact.

---

## Action Classification

Actions should be grouped into the following categories.

### A01. Tree and planning actions

- create nodes
- create children
- define layouts
- revise layouts
- inspect hierarchy

### A02. Run-control actions

- start work
- pause work
- resume work
- cancel work
- retry work

### A03. Session actions

- bind session
- attach to session
- resume session
- nudge session
- push child session
- pop child session

### A04. Workflow and subtask actions

- inspect workflow
- inspect tasks/subtasks
- retrieve prompts/context
- mark subtask progress
- register summaries

### A05. Review/validation/testing actions

- inspect validation
- inspect review
- inspect testing
- trigger review or hook execution where allowed

### A06. Git and rebuild actions

- inspect branch/seed/final state
- regenerate node
- rectify upstream
- approve merge
- inspect merge history/conflicts

### A07. Documentation and provenance actions

- build docs
- inspect docs
- inspect provenance
- inspect rationale

### A08. YAML/config actions

- inspect source YAML
- inspect resolved YAML
- inspect overrides
- validate YAML
- inspect hooks

---

## Automation Matrix

| Action ID | User-Visible Action | Candidate CLI Surface | Runtime Owner | DB Impact | Audit Surface | Current Coverage | Gaps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ACT-001 | Create top-level node | `ai-tool node create ...` | node creation runtime | new `node_versions`, source/compiled workflow rows | node lineage, prompts, workflow history | missing | Create command and persistence semantics not yet fully specified. |
| ACT-002 | Create child node manually | `ai-tool node child create ...` | node creation runtime | new child `node_versions`, `node_children`, maybe `node_dependencies` | tree/history views | missing | Manual creation path still needs concrete CLI and validation rules. |
| ACT-003 | Generate child layout | `ai-tool layout generate --node <id>` | node run/subtask handler | updated layout artifact, summary, prompt history | prompt history, source docs, summaries | partially covered | Needs final command semantics and persisted artifact contract. |
| ACT-004 | Review child layout | `ai-tool review run --node <id> --scope layout` | review runtime | review result rows, summaries | review history | missing | Review execution CLI and result model need formalization. |
| ACT-005 | Edit or replace a layout | `ai-tool layout update --node <id> --file <path>` | config/update runtime | new source docs, rebuild trigger maybe | source lineage, rebuild history | missing | Layout update semantics and rebuild trigger rules are not frozen. |
| ACT-006 | Show subtree | `ai-tool tree show --node <id>` | read-only CLI | none | CLI output only | covered | Already present conceptually. |
| ACT-007 | Show ancestors/children/siblings | `ai-tool node ancestors|children|siblings ...` | read-only CLI | none | CLI output only | covered | Already present conceptually. |
| ACT-008 | Show dependency state | `ai-tool node dependency-status --node <id>` | read-only CLI | none | dependency views | partially covered | DB/view details still need strengthening. |
| ACT-009 | Start/admit a node run | `ai-tool node run start --node <id>` or `ai-tool node resume --node <id>` | run admission runtime | new `node_runs`, `node_run_state`, maybe `sessions` | node run history | missing | Explicit start semantics are not yet frozen. |
| ACT-010 | Pause a node | `ai-tool node pause --node <id>` | run control runtime | update run state, node lifecycle state, maybe pause event | pause history, summaries | partially covered | Historical pause-event structure may be missing. |
| ACT-011 | Resume a node | `ai-tool node resume --node <id>` | run control/runtime recovery | update run state/session state | run/session history | partially covered | Resume semantics depend on unfinished recovery design. |
| ACT-012 | Cancel a node | `ai-tool node cancel --node <id>` | run control runtime | update lifecycle/run/session status | run history, session events | partially covered | Cancel side effects and allowed states need stronger rules. |
| ACT-013 | Retry current subtask | `ai-tool subtask retry --node <id>` | failure handling runtime | new `subtask_attempts`, updated cursor state | attempt history | partially covered | Eligibility rules still need explicit pseudocode. |
| ACT-014 | Show node summary | `ai-tool node show --node <id>` | read-only CLI | none | CLI output only | covered | Present in CLI spec. |
| ACT-015 | Show node runs | `ai-tool node runs --node <id>` | read-only CLI | none | run history | covered | Present in CLI spec. |
| ACT-016 | Show current task/subtask | `ai-tool task current`, `ai-tool subtask current` | read-only CLI | none | current cursor views | covered | Present in CLI spec. |
| ACT-017 | Show workflow | `ai-tool workflow show --node <id>` | read-only CLI | none | compiled workflow tables | covered | Present in CLI spec. |
| ACT-017A | Show compiled subtask chain with execution state | `ai-tool workflow chain --node <id>` / `--run <id>` | read-only CLI | none | compiled workflow tables, run cursor state, subtask attempt history | covered | Present in CLI spec; should support structure-only and run-aware views. |
| ACT-018 | Retrieve current prompt | `ai-tool subtask prompt --node <id>` | session/runtime CLI | none | prompt history | covered | Present conceptually; result shape still needs finalization. |
| ACT-019 | Retrieve current context | `ai-tool subtask context --node <id>` | session/runtime CLI | none | context view/history | partially covered | Context composition contract still needs full definition. |
| ACT-020 | Mark subtask start | `ai-tool subtask start --compiled-subtask <id>` | session or runtime supervisor | update current attempt state, session heartbeat | attempt history, session events | covered | Present conceptually; ownership needs freezing. |
| ACT-021 | Mark subtask heartbeat | `ai-tool subtask heartbeat --compiled-subtask <id>` | session runtime | update heartbeat/session state | session events | covered | Present conceptually. |
| ACT-022 | Mark subtask complete | `ai-tool subtask complete --compiled-subtask <id>` | session or runtime supervisor | update attempt status, cursor | attempt history, cursor history | covered | Ownership and side effects still need full runtime freeze. |
| ACT-023 | Mark subtask failed | `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>` | session/runtime failure handler | update attempt/run/node state, summary rows | summaries, failure history | covered | Parent failure propagation remains incomplete. |
| ACT-024 | Register summary | `ai-tool summary register --node <id> --file <path> --type <type>` | session/runtime | new `summaries` rows | summary history | covered | Summary taxonomy needs tighter design. |
| ACT-025 | Show summaries | `ai-tool summary show|list ...` | read-only CLI | none | summary tables | covered | Present conceptually. |
| ACT-026 | Show validation results | `ai-tool validation show --node <id>` | read-only CLI | none | validation tables/views | partially covered | Dedicated result model may be missing. |
| ACT-027 | Show review results | `ai-tool review show --node <id>` | read-only CLI | none | review tables/views | partially covered | Dedicated review result model may be missing. |
| ACT-028 | Show test results | likely `ai-tool testing show --node <id>` | read-only CLI | none | test result tables/views | missing | Testing surface needs formalization. |
| ACT-029 | Run hooks manually where allowed | `ai-tool hooks run --node <id> --event <event>` | runtime/hook engine | hook execution records, maybe summaries | hook history, summaries | partially covered | Hook execution audit model still needs detail. |
| ACT-030 | Show source YAML | `ai-tool yaml show --node <id>` | read-only CLI | none | source docs | covered | Present conceptually. |
| ACT-031 | Show resolved YAML | `ai-tool yaml resolved --node <id>` | read-only CLI | none | compiled/resolved docs | covered | Present conceptually. |
| ACT-032 | Validate YAML | `ai-tool yaml validate --path <file>` | validation runtime | possibly validation result rows if persisted | validation history | partially covered | Should decide whether ad hoc validation becomes auditable history. |
| ACT-033 | Show overrides | `ai-tool overrides list|show --node <id>` | read-only CLI | none | source lineage | covered | Present conceptually. |
| ACT-034 | Show hooks in effect | `ai-tool hooks list|show --node <id>` | read-only CLI | none | workflow/hook lineage | covered | Present conceptually. |
| ACT-035 | Show branch info | `ai-tool git branch show --node <id>` | read-only CLI | none | branch/git metadata | covered | Present conceptually. |
| ACT-036 | Show seed/final commits | `ai-tool git seed show`, `ai-tool git final show` | read-only CLI | none | node/git metadata | covered | Present conceptually. |
| ACT-037 | Reset node to seed | `ai-tool git reset-node-to-seed --node <id>` | rectification runtime | git metadata, maybe workflow event rows | rebuild/merge audit | partially covered | Operator guardrails and allowed call contexts need rules. |
| ACT-038 | Merge current children | `ai-tool git merge-current-children --node <id> --ordered` | rectification runtime | merge events/conflicts | merge history | covered | Present conceptually; conflict semantics still need refinement. |
| ACT-039 | Finalize node git state | `ai-tool git finalize-node --node <id>` | finalization runtime | final commit fields, run/node status | run history, node version history | partially covered | Exact finalize side effects need canonical ordering. |
| ACT-040 | Regenerate a node | `ai-tool node regenerate --node <id>` | rebuild runtime | new node versions, rebuild events, maybe new runs | rebuild history, lineage | covered | Present conceptually; cutover timing still needs detail. |
| ACT-041 | Rectify upstream | `ai-tool node rectify-upstream --node <id>` | rebuild runtime | rebuild events, merge events, run history | rebuild and merge history | covered | Present conceptually; ancestor failure handling still needs detail. |
| ACT-042 | Show rebuild history | `ai-tool rebuild show --node <id>` | read-only CLI | none | rebuild events | partially covered | CLI concept exists; exact shape likely needs expansion. |
| ACT-043 | Show merge events/conflicts | `ai-tool merge-events show`, `ai-tool merge-conflicts show` | read-only CLI | none | merge tables | covered | Present conceptually. |
| ACT-044 | Approve merge to parent/base | `ai-tool merge approve --node <id>` / `merge parent` / `merge base` | gated merge runtime | lifecycle/run status, maybe gate events | summaries, merge history | partially covered | Gate event model and safety rules still need detail. |
| ACT-045 | Show sessions | `ai-tool session show|list ...` | read-only CLI | none | sessions/session events | covered | Present conceptually. |
| ACT-046 | Attach to session | `ai-tool session attach --node <id>` | session runtime | maybe session event | session events | covered | Present conceptually. |
| ACT-047 | Resume session | `ai-tool session resume --node <id>` | recovery runtime | update or create sessions, session events | session history | partially covered | Depends on unresolved recovery semantics. |
| ACT-048 | Nudge idle session | `ai-tool session nudge --node <id>` | session/runtime | session events, maybe summaries | session history | covered | Present conceptually; escalation rules still missing. |
| ACT-049 | Push child session | `ai-tool session push --node <id> --reason <reason>` | session orchestration runtime | new child session rows/events | session history, summaries | covered | Present conceptually; merge-back semantics still need definition. |
| ACT-050 | Pop child session | `ai-tool session pop --session <id> --summary-file <path>` | session orchestration runtime | session completion, summary registration | session history, summaries | covered | Present conceptually; data contract needs precision. |
| ACT-051 | Build node docs | `ai-tool docs build-node-view --node <id>` | docs runtime | new `node_docs`, maybe summaries | docs history | covered | Present conceptually; source/input blend still needs detail. |
| ACT-052 | Build tree docs | `ai-tool docs build-tree --node <id>` | docs runtime | new `node_docs` rows | docs history | covered | Present conceptually. |
| ACT-053 | Show docs | `ai-tool docs list|show ...` | read-only CLI | none | docs tables | covered | Present conceptually. |
| ACT-054 | Show prompt lineage | `ai-tool prompts list|show ...` | read-only CLI | none | prompt tables | covered | Present conceptually. |
| ACT-055 | Show rationale | `ai-tool rationale show --node <id>` | read-only CLI | none | provenance/rationale surfaces | partially covered | Rationale query model needs more concrete backing. |
| ACT-056 | Show entity history/relations | `ai-tool entity show|history|relations|changed-by ...` | read-only CLI | none | entity and relation tables | covered | Present conceptually; provenance identity remains unresolved. |
| ACT-057 | Update project policy/override | likely `ai-tool policy update ...` or file-edit + compile flow | config/update runtime | new source docs, possible rebuild event | source lineage, rebuild history | missing | Policy update automation is not yet fully specified. |
| ACT-058 | Validate dependency graph | `ai-tool node dependency-validate --node <id>` | validation/runtime | validation result rows | validation history | partially covered | Surface now exists in the CLI spec; result persistence and exact semantics still need canonicalization. |
| ACT-059 | Inspect current blockers | `ai-tool node blockers --node <id>` | read-only CLI | none | dependency/cursor views | covered | Present in the CLI spec; backing views still need implementation detail. |
| ACT-060 | Inspect active pause gate | `ai-tool node pause-state --node <id>` | read-only CLI | none | pause/current-state views | covered | Present in the CLI spec; event-history depth still depends on the workflow-event model. |

---

## Action Families With Weakest Coverage

The current weakest action families are:

### 1. Planning/editing actions

Creation, update, and revision flows for nodes, layouts, and policies are still not fully mapped to CLI and rebuild semantics.

### 2. Review/testing actions

Read surfaces partly exist, but execution, persistence, and mutation surfaces are incomplete.

### 3. Pause/gating introspection

The user will need better visibility into why work is blocked or paused.

### 4. Dependency/operator diagnostic actions

Blocker inspection, invalid dependency detection, and readiness inspection need stronger CLI mapping.

---

## Likely Missing CLI Surfaces

Based on this matrix, the following CLI surfaces should likely be added or formalized:

- `ai-tool node create ...`
- `ai-tool node child create ...`
- `ai-tool layout generate ...`
- `ai-tool layout update ...`
- `ai-tool review run ...`
- `ai-tool testing show ...`
- `ai-tool policy update ...`
- `ai-tool node dependency-validate ...`
- `ai-tool node blockers ...`
- `ai-tool node pause-state ...`

These names may change, but these capabilities likely need explicit automation paths.

---

## Likely Missing Durable Structures

This matrix also suggests the likely need for:

- review result persistence
- test result persistence
- pause/gate event persistence
- richer action audit history for mutable operator actions

---

## Recommended Next Resolution Steps

The best next follow-on work from this matrix is:

1. create `notes/auditability_checklist.md`
2. create `notes/review_testing_docs_yaml_plan.md`
3. update the future v2 CLI spec to include the missing action surfaces
4. update the future DB v2 spec with any needed result/event tables

---

## Exit Criteria

This action automation pass should be considered complete when:

- every meaningful user-visible action has an automation path
- gaps are explicit for actions that do not yet have CLI/runtime/DB backing
- missing audit and persistence needs are identified

At that point, the “everything user-can-do is automatable” goal becomes concrete enough to evaluate during v2 rewrite.
