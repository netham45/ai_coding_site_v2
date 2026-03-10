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

- `notes/explorations/original_concept.md`
- `notes/archive/superseded/cli_surface_spec_revised.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

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
| ACT-001 | Create top-level node | `ai-tool node create ...` | node creation runtime | new hierarchy rows, `node_versions`, source lineage, optional compiled workflow rows after later compile | node lineage, sources, workflow history | covered | `node create` is now daemon-backed and durable; workflow compilation remains an explicit follow-on action. |
| ACT-002 | Create child node manually | `ai-tool node child create ...` | node creation runtime | new child hierarchy rows, `node_children`, `parent_child_authority`, `node_versions`, optional dependency rows | tree/history views, child-materialization inspection | covered | Manual child creation now routes through the same durable authority model as auto-materialized children. |
| ACT-003 | Generate child layout | `ai-tool layout generate --node <id>` | node run/subtask handler | updated layout artifact, summary, prompt history | prompt history, source docs, summaries | partially covered | Needs final command semantics and persisted artifact contract. |
| ACT-004 | Review child layout | `ai-tool review run --node <id> --scope layout` | review runtime | review result rows, summaries | review history | missing | Review execution CLI and result model need formalization. |
| ACT-005 | Edit or replace a layout | `ai-tool layout update --node <id> --file <path>` | config/update runtime | new source docs, rebuild trigger maybe | source lineage, rebuild history | missing | Layout update semantics and rebuild trigger rules are not frozen. |
| ACT-006 | Show subtree | `ai-tool tree show --node <id>` | read-only CLI | none | CLI output only | covered | Already present conceptually. |
| ACT-007 | Show ancestors/children/siblings | `ai-tool node ancestors|children|siblings ...` | read-only CLI | none | CLI output only | covered | Already present conceptually. |
| ACT-008 | Show dependency state | `ai-tool node dependency-status --node <id>` | read-only CLI | none | dependency views | partially covered | DB/view details still need strengthening. |
| ACT-009 | Start/admit a node run | `ai-tool node run start --node <id>` or `ai-tool node resume --node <id>` | run admission runtime | new `node_runs`, `node_run_state`, maybe `sessions` | node run history, workflow events | covered | Start/admit now persists durable run rows and workflow-event history through daemon admission logic. |
| ACT-010 | Pause a node | `ai-tool node pause --node <id>` | run control runtime | update run state, node lifecycle state, workflow event rows | pause history, summaries, workflow events | covered | Pause state and workflow-event audit are now durable; later work is about richer policy, not missing control. |
| ACT-011 | Resume a node | `ai-tool node resume --node <id>` | run control/runtime recovery | update run state/session state, workflow event rows | run/session/workflow-event history | covered | Resume and recovery are daemon-backed and durable. |
| ACT-012 | Cancel a node | `ai-tool node cancel --node <id>` / `ai-tool workflow cancel --node <id>` | run control runtime | update lifecycle/run/session status and authority rows | workflow events, daemon mutation events, session events | covered | Cancel now has a real daemon-backed mutation path with durable authority and workflow-event audit; allowed states remain bounded to active runs only. |
| ACT-013 | Retry current subtask | `ai-tool subtask retry --node <id>` / `--attempt <id>` | failure handling runtime | new `subtask_attempts`, updated cursor state, reopened `node_runs` state when applicable | attempt history, workflow events | covered | Retry now creates a fresh durable attempt on the latest retryable run and exposes conflict errors when the current subtask is already running. |
| ACT-014 | Show node summary | `ai-tool node show --node <id>` | read-only CLI | none | CLI output only | covered | Present in CLI spec. |
| ACT-015 | Show node runs | `ai-tool node runs --node <id>` | read-only CLI | none | run history | covered | Present in CLI spec. |
| ACT-016 | Show current task/subtask | `ai-tool task current`, `ai-tool subtask current` | read-only CLI | none | current cursor views | covered | `task current --node <id>`, `task list --node <id>`, `subtask current --node <id>`, and `subtask list --node <id>` now project the current compiled workflow plus durable lifecycle cursor into operator-facing read surfaces. |
| ACT-017 | Show workflow | `ai-tool workflow show --node <id>` | read-only CLI | none | compiled workflow tables | covered | Present in CLI spec. |
| ACT-017A | Show compiled subtask chain with execution state | `ai-tool workflow chain --node <id>` / `--run <id>` | read-only CLI | none | compiled workflow tables, run cursor state, subtask attempt history | covered | Present in CLI spec; should support structure-only and run-aware views. |
| ACT-018 | Retrieve current prompt | `ai-tool subtask prompt --node <id>` | session/runtime CLI | none | prompt history | covered | Present conceptually; result shape still needs finalization. |
| ACT-019 | Retrieve current context | `ai-tool subtask context --node <id>` | session/runtime CLI | none | context view/history | covered | The daemon now returns a structured stage-context bundle with startup, dependency, history, and reconcile metadata. |
| ACT-020 | Mark subtask start | `ai-tool subtask start --compiled-subtask <id>` | daemon run orchestration | update current attempt state, session heartbeat | attempt history, session events | covered | Start is daemon-owned and durably updates attempt state. |
| ACT-021 | Mark subtask heartbeat | `ai-tool subtask heartbeat --compiled-subtask <id>` | session runtime | update heartbeat/session state | session events | covered | Present conceptually. |
| ACT-022 | Mark subtask complete | `ai-tool subtask complete --compiled-subtask <id>` | daemon run orchestration | update attempt status, cursor | attempt history, cursor history, workflow events | covered | Completion is daemon-owned and durably advances the runtime state model. |
| ACT-023 | Mark subtask failed | `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>` | session/runtime failure handler | update attempt/run/node state, summary rows | summaries, failure history | covered | Parent failure propagation remains incomplete. |
| ACT-024 | Register summary | `ai-tool summary register --node <id> --file <path> --type <type>` | session/runtime | new `summaries` rows | summary history | covered | Summary taxonomy needs tighter design. |
| ACT-025 | Show summaries | `ai-tool summary show|list ...` | read-only CLI | none | summary tables | covered | Present conceptually. |
| ACT-026 | Show validation results | `ai-tool validation show --node <id>` | read-only CLI | none | validation tables/views | covered | Validation summaries and result history are daemon-backed and durable. |
| ACT-027 | Show review results | `ai-tool review show --node <id>` | read-only CLI | none | review tables/views | covered | Review summaries and result history are daemon-backed and durable. |
| ACT-028 | Show test results | `ai-tool testing show --node <id>` | read-only CLI | none | test result tables/views | covered | `testing show`, `testing results`, and `testing run` are now daemon-backed; default built-in workflows still stage testing behind explicit task/policy/override selection. |
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
| ACT-042 | Show rebuild history | `ai-tool rebuild show --node <id>` / `ai-tool node rebuild-history --node <id>` | read-only CLI | none | rebuild events | covered | `rebuild show` is now an explicit alias over the daemon-backed rebuild-history read path. |
| ACT-043 | Show merge events/conflicts | `ai-tool merge-events show`, `ai-tool merge-conflicts show` | read-only CLI | none | merge tables | covered | Present conceptually. |
| ACT-044 | Approve merge to parent/base | `ai-tool merge approve --node <id>` / `merge parent` / `merge base` | gated merge runtime | lifecycle/run status, maybe gate events | summaries, merge history | partially covered | Gate event model and safety rules still need detail. |
| ACT-045 | Show sessions | `ai-tool session show|list ...` | read-only CLI | none | sessions/session events | covered | Present conceptually. |
| ACT-046 | Attach to session | `ai-tool session attach --node <id>` | session runtime | maybe session event | session events | covered | Present conceptually. |
| ACT-047 | Resume session | `ai-tool session resume --node <id>` | recovery runtime | update or create sessions, session events | session history | covered | Recovery classification and recommended actions are implemented; resume is a real daemon-backed flow. |
| ACT-048 | Nudge idle session | `ai-tool session nudge --node <id>` | session/runtime | session events, maybe summaries | session history | covered | Present conceptually; escalation rules still missing. |
| ACT-049 | Push child session | `ai-tool session push --node <id> --reason <reason>` | session orchestration runtime | new child session rows/events | session history, summaries | covered | Present conceptually; merge-back semantics still need definition. |
| ACT-050 | Pop child session | `ai-tool session pop --session <id> --summary-file <path>` | session orchestration runtime | session completion, summary registration | session history, summaries | covered | Present conceptually; data contract needs precision. |
| ACT-051 | Build node docs | `ai-tool docs build-node-view --node <id>` | docs runtime | new `documentation_outputs` rows, maybe summaries | docs history | covered | Docs builds are now durably stored in `documentation_outputs` rather than ephemeral render-only artifacts. |
| ACT-052 | Build tree docs | `ai-tool docs build-tree --node <id>` | docs runtime | new `documentation_outputs` rows | docs history | covered | Tree docs follow the same append-only durable output model. |
| ACT-053 | Show docs | `ai-tool docs list|show ...` | read-only CLI | none | docs tables | covered | Present conceptually. |
| ACT-054 | Show prompt lineage | `ai-tool prompts list|show ...` | read-only CLI | none | prompt tables | covered | Present conceptually. |
| ACT-055 | Show rationale | `ai-tool rationale show --node <id>` | read-only CLI | none | provenance/rationale surfaces | covered | Rationale reads are backed by durable provenance refresh results and entity-change history. |
| ACT-056 | Show entity history/relations | `ai-tool entity show|history|relations|changed-by ...` | read-only CLI | none | entity and relation tables | covered | Present conceptually; provenance identity remains unresolved. |
| ACT-057 | Update project policy/override | likely `ai-tool policy update ...` or file-edit + compile flow | config/update runtime | new source docs, possible rebuild event | source lineage, rebuild history | missing | Policy update automation is not yet fully specified. |
| ACT-058 | Validate dependency graph | `ai-tool node dependency-validate --node <id>` | validation/runtime | dependency blocker rows and readiness state, no separate validation row family | blocker/readiness history | covered | Dependency validation is implemented as a daemon-owned readiness and legality check with durable blocker state, not a separate validation-results family. |
| ACT-059 | Inspect current blockers | `ai-tool node blockers --node <id>` | read-only CLI | none | dependency/cursor views | covered | Present in the CLI spec; backing views still need implementation detail. |
| ACT-060 | Inspect active pause gate | `ai-tool node pause-state --node <id>` | read-only CLI | none | pause/current-state views | covered | Present in the CLI spec; event-history depth still depends on the workflow-event model. |

---

## Action Families With Weakest Coverage

The current weakest action families are:

### 1. Planning/editing actions

Layout generation/update and project-policy mutation still need final operator-safe write semantics even though node creation itself is now daemon-backed and durable.

### 2. Planning/config mutation actions

Layout generation and update plus project-policy mutation still do not have the same daemon-backed operational surface quality as the runtime control families.

### 3. Live git and finalize actions

Durable merge, rebuild, and branch metadata exist, but safe working-tree execution commands are still intentionally deferred.

---

## Likely Missing CLI Surfaces

Based on this matrix, the following CLI surfaces should likely be added or formalized:

- `ai-tool node create ...`
- `ai-tool node child create ...`
- `ai-tool layout generate ...`
- `ai-tool layout update ...`
- `ai-tool review run ...`
- `ai-tool policy update ...`

These names may change, but these capabilities likely need explicit automation paths.

---

## Likely Missing Durable Structures

This matrix still suggests the likely need for:

- richer layout and policy mutation audit once those write surfaces exist
- stronger live git action audit once working-tree execution lands
- broader provenance extractor coverage if non-Python assets become first-class

---

## Recommended Next Resolution Steps

The best next follow-on work from this matrix is:

1. formalize daemon-backed layout generation and layout update surfaces
2. formalize project-policy update and rebuild-trigger semantics
3. land the safe live-git execution layer for reset/merge/finalize actions
4. keep folding implementation decisions back into the canonical v2 specs so the matrix can shed `exists_but_needs_fold_in` states

---

## Exit Criteria

This action automation pass should be considered complete when:

- every meaningful user-visible action has an automation path
- gaps are explicit for actions that do not yet have CLI/runtime/DB backing
- missing audit and persistence needs are identified

At that point, the “everything user-can-do is automatable” goal becomes concrete enough to evaluate during v2 rewrite.
