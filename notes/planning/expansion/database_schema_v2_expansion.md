# Database Schema V2 Expansion Plan

## Purpose

This document expands the database design from conceptual table structure into a more implementation-grade schema planning artifact.

The primary goal is to identify:

- all durable entities that must exist
- the constraints they need
- the indexes they need
- the lifecycle/value models they need
- the integrity rules that SQL can enforce directly
- the integrity rules that application logic must enforce

This is not yet the final canonical v2 schema spec. It is the expansion and hardening plan that should feed into `notes/specs/database/database_schema_spec_v2.md`.

Related documents:

- `notes/archive/superseded/database_schema_spec_revised.md`
- `notes/planning/expansion/full_spec_expansion_plan.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`

---

## Goals

The database layer should satisfy the following.

### 1. The database is the durable canonical record

No critical runtime variable should exist only in memory if it affects execution, debugging, reproducibility, or auditability.

The database is not the live orchestration authority.

Recommended architecture:

- the daemon owns live coordination and orchestration decisions
- the database stores the durable state and history required for recovery, auditability, and inspection

### 2. Versioned entities should not be mutated in place

The system should prefer new durable rows representing new versions or new attempts rather than rewriting history.

### 3. Current state and history must both be queryable

The schema should support:

- current operational queries
- history/audit queries
- lineage traversal
- recovery/resume queries

### 4. State models should be explicit

Statuses, lifecycle states, dependency states, and run states should not remain loose free-form text unless there is a strong reason.

### 5. The schema should support implementation without hidden assumptions

If the runtime depends on something being unique, ordered, resumable, or derivable, the schema or views should make that explicit.

---

## Database Entity Families

The schema can be grouped into the following families.

### D01. Hierarchy and versioning

- `logical_node_current_versions`
- `node_versions`
- `node_children`
- `parent_child_authority`
- `node_dependencies`
- `node_version_lineage`
- `rebuild_events`

### D02. Source and compilation

- `source_documents`
- `compiled_workflows`
- `compiled_workflow_sources`
- `compiled_tasks`
- `compiled_subtasks`
- `compiled_subtask_dependencies`
- `compiled_subtask_checks`

### D03. Execution and runtime state

- `node_runs`
- `node_run_state`
- `subtask_attempts`
- `sessions`
- `session_events`
- `child_session_results`
- `workflow_events`

### D04. Git lineage and rectification

- `merge_events`
- `merge_conflicts`

### D05. Prompts, summaries, reviews, validation, testing, docs

- `prompts`
- `summaries`
- `node_docs`
- additional review/validation/testing result tables likely needed

### D06. Provenance and rationale

- `code_entities`
- `node_entity_changes`
- `code_relations`

### D07. Current-state query surfaces

- `active_node_versions`
- `latest_node_runs`
- `latest_subtask_attempts`
- additional views likely needed

---

## Areas That Need Stronger V2 Definition

The current database spec is directionally strong, but these areas need more precise design.

### 1. Value constraints

Many columns currently use `text` where the allowed values are conceptually bounded.

### 2. Indexing strategy

The current spec names tables well, but does not yet define enough of the indexes needed for operational queries.

### 3. Current-state uniqueness rules

The design implies one authoritative version, one latest-created version, one active run, one active primary session, and one current cursor, and these assumptions need stronger modeling.

### 4. Review/validation/testing persistence

The current spec references these behaviors, but dedicated result structures are still underdefined.

### 5. Session model detail

The session tables exist, but parent session vs pushed child session modeling still needs clearer constraints, and current primary-session identity should not be duplicated on `node_runs`.

### 6. Authoritative versus candidate lineage

The cutover notes require a stable distinction between:

- latest created version
- authoritative current version
- candidate rebuild parent/child edges

That distinction should be modeled explicitly rather than inferred weakly from `status`.

### 7. Provenance identity stability

The code entity model needs a stronger identity and uniqueness strategy.

### 8. State transition enforcement

Some transitions may need application-enforced guards or append-only event logs in addition to current-state tables.

---

## Recommended Value-Model Strategy

The following guidance should be used during v2 DB work.

### Use constrained text or domains where practical

For bounded operational states, avoid unconstrained free-form text.

Candidates include:

- node lifecycle state
- node run status
- session status
- summary type
- prompt role
- dependency type
- merge conflict resolution status
- subtask type
- validation check type

### Use JSON only where the shape is truly extensible

JSON is appropriate for:

- compiled config blobs
- execution cursor detail
- validation detail payloads
- source or event payloads

JSON should not be used to avoid modeling obviously relational concepts.

---

## Table-By-Table Expansion Notes

## 0. `logical_node_current_versions`

### Current role

Stores the authoritative current version and latest-created version for each logical node.

### Important constraints

- one row per `logical_node_id`
- both referenced versions must belong to the same logical node

### Important indexes

- index on `authoritative_node_version_id`
- index on `latest_created_node_version_id`

### Application-enforced rules

- cutover should update authoritative selection atomically with related supersession state

## 1. `node_versions`

### Current role

Represents the durable versioned identity of a node.

### Additional fields or rules to consider

- enforce legal values for `status`
- consider `is_top_level boolean` if parent-null checks are frequent
- consider `branch_generation_number integer`
- consider `logical_path text` for deterministic hierarchy addressing if needed

### Important constraints

- unique `(logical_node_id, version_number)`
- version numbers should increase monotonically per logical node
- a node should not supersede itself
- `supersedes_node_version_id` should likely be unique if one old version can only be directly superseded once

### Important indexes

- index on `logical_node_id`
- index on `parent_node_version_id`
- index on `status`
- index on `supersedes_node_version_id`
- index on `active_branch_name`

### Application-enforced rules

- only one authoritative version per logical node through `logical_node_current_versions`
- old versions should not become active again once superseded without an explicit recovery procedure

---

## 2. `node_children`

### Current role

Represents parent-child version edges in the active tree.

### Additional fields or rules to consider

- `child_key text` if a layout-defined identity is needed
- `created_at timestamptz`
- `origin_type text` for manual versus layout-generated child tracking

### Important constraints

- prevent parent = child
- enforce one parent per child version if the model forbids multiple parents
- if `ordinal` is used for layout order, consider uniqueness per parent when present

### Important indexes

- index on `parent_node_version_id`
- index on `child_node_version_id`
- composite index on `(parent_node_version_id, ordinal)`

### Application-enforced rules

- prevent cycles
- ensure child tier/kind is valid under parent constraints

## 2A. `parent_child_authority`

### Current role

Stores whether a parent's child set is manual, layout-authoritative, or hybrid.

### Important constraints

- one row per parent node version
- `authority_mode` should be bounded

### Important indexes

- index on `authority_mode`
- index on `authoritative_layout_hash`

### Application-enforced rules

- hybrid trees should block silent structural rematerialization

---

## 3. `node_dependencies`

### Current role

Represents dependency edges allowed between siblings or parent-owned children.

### Additional fields or rules to consider

- `dependency_status text` if caching dependency state is useful
- `blocking_reason text` only if persisted blocking explanations are needed

## 3A. `node_version_lineage`

### Current role

Stores authoritative and candidate parent/child lineage edges separately.

### Important constraints

- constrain `lineage_scope`
- prevent parent = child

### Important indexes

- index on `(parent_node_version_id, lineage_scope)`
- index on `(child_node_version_id, lineage_scope)`

### Application-enforced rules

- authoritative dependency resolution should use authoritative lineage only
- candidate lineage should remain queryable without affecting default scheduling before cutover

### Important constraints

- `dependency_type` should be constrained to allowed values
- prevent self-dependency
- unique `(node_version_id, depends_on_node_version_id)`

### Important indexes

- index on `node_version_id`
- index on `depends_on_node_version_id`
- composite index on `(node_version_id, required_state)`

### Application-enforced rules

- parent dependencies are not allowed
- cousin/nibling dependencies are not allowed
- dependency target must be sibling or child as allowed by hierarchy rules

---

## 4. `source_documents`

### Current role

Stores YAML source documents used for workflow compilation.

### Additional fields or rules to consider

- `source_scope text` such as built-in, project-extension, project-override
- `is_active boolean` if historical archival and current sets need distinction

### Important constraints

- constrain `doc_family`
- enforce uniqueness on `(path, content_hash)` if duplicates should collapse

### Important indexes

- index on `doc_family`
- index on `path`
- index on `content_hash`

### Application-enforced rules

- path resolution and override precedence belong in compile logic

---

## 5. `compiled_workflows`

### Current role

Stores immutable compiled workflow snapshots.

### Additional fields or rules to consider

- `compile_status text`
- `compiled_from_node_definition_id text` if useful for reporting
- `workflow_version integer` if schema evolution across runtime versions matters

### Important constraints

- ideally one workflow row per compilation event
- `source_hash` should be non-null and stable

### Important indexes

- index on `node_version_id`
- index on `source_hash`
- index on `created_at`

### Application-enforced rules

- active runs should reference exactly one compiled workflow
- historical runs must continue pointing at the workflow they used

---

## 6. `compiled_tasks`

### Current role

Stores compiled task instances for a workflow.

### Additional fields or rules to consider

- `task_kind text` if useful
- `source_task_definition_id text`

### Important constraints

- unique `(compiled_workflow_id, task_key)`
- unique `(compiled_workflow_id, ordinal)`

### Important indexes

- index on `compiled_workflow_id`
- composite index on `(compiled_workflow_id, ordinal)`

---

## 7. `compiled_subtasks`

### Current role

Stores compiled executable subtask instances with durable IDs.

### Additional fields or rules to consider

- `status_model text` only if subtask type families diverge significantly
- `source_file_path text`
- `source_hash text`

### Important constraints

- `subtask_type` should be constrained
- unique `(compiled_task_id, ordinal)`
- source keys may or may not be unique within a workflow depending on reuse strategy

### Important indexes

- index on `compiled_workflow_id`
- index on `compiled_task_id`
- index on `subtask_type`
- composite index on `(compiled_task_id, ordinal)`

### Application-enforced rules

- resolved prompts/commands should be immutable once compiled

---

## 8. `compiled_subtask_dependencies`

### Current role

Stores dependency edges between compiled subtask instances.

### Important constraints

- prevent self-dependency

### Important indexes

- index on `compiled_subtask_id`
- index on `depends_on_compiled_subtask_id`

### Application-enforced rules

- dependency graph should be acyclic

---

## 9. `compiled_subtask_checks`

### Current role

Stores compiled validation checks attached to compiled subtask instances.

### Additional fields or rules to consider

- `source_check_id text`
- `severity text`

### Important constraints

- `check_type` should be constrained
- unique `(compiled_subtask_id, ordinal)`

### Important indexes

- index on `compiled_subtask_id`
- index on `check_type`

---

## 10. `node_runs`

### Current role

Represents execution attempts for node versions.

### Additional fields or rules to consider

- `run_kind text` such as normal, rebuild, recovery, review-only
- `failure_reason text`

### Important constraints

- unique `(node_version_id, run_number)`
- constrain `run_status`

### Important indexes

- index on `node_version_id`
- index on `compiled_workflow_id`
- index on `run_status`
- composite index on `(node_version_id, run_number desc)`

### Application-enforced rules

- likely only one active run per node version
- ended runs should not regain running status without explicit recovery semantics

---

## 11. `node_run_state`

### Current role

Stores the current operational cursor and execution state for a run.

### Additional fields or rules to consider

- `current_phase text` if useful for UI summaries
- `waiting_on_node_version_id uuid` if a single primary blocker is worth storing

### Important constraints

- constrain `lifecycle_state`
- `current_subtask_attempt` should be positive when present
- failure counters should not be negative

### Important indexes

- index on `lifecycle_state`
- index on `current_task_id`
- index on `current_compiled_subtask_id`
- index on `pause_flag_name`

### Application-enforced rules

- `current_task_id` and `current_compiled_subtask_id` must belong to the run's compiled workflow
- cursor advancement must respect dependency checks

---

## 12. `subtask_attempts`

### Current role

Stores each execution attempt for each compiled subtask in a node run.

### Additional fields or rules to consider

- `attempt_kind text`
- `failure_class text`
- `validation_passed boolean`

### Important constraints

- unique `(node_run_id, compiled_subtask_id, attempt_number)`
- constrain `status`

### Important indexes

- index on `node_run_id`
- index on `compiled_subtask_id`
- index on `status`
- composite index on `(node_run_id, compiled_subtask_id, attempt_number desc)`

---

## 13. `sessions`

### Current role

Represents runtime sessions, including primary node sessions and optional pushed child sessions.

### Additional fields or rules to consider

- `session_role text` such as primary or pushed-child
- `parent_session_id uuid references sessions(id)` for pushed-child sessions
- `node_run_id uuid references node_runs(id)` if session-to-run binding should be explicit here
- `resume_token text` if provider recovery requires it

### Important constraints

- constrain `status`
- if `session_role = primary`, parent session should be null
- if `session_role = pushed_child`, parent session should be non-null

### Important indexes

- index on `node_version_id`
- index on `node_run_id` if added
- index on `provider_session_id`
- index on `tmux_session_name`
- index on `status`
- index on `parent_session_id`

### Application-enforced rules

- only one active primary session per active run
- pushed child sessions should not become git owners

Recommended stance:

- `sessions` is the canonical owner of current primary-session identity
- `node_runs` should not duplicate that ownership with a `session_id` column

---

## 14. `session_events`

### Current role

Stores append-only session lifecycle and activity events.

### Additional fields or rules to consider

- constrain `event_type`

### Important indexes

- index on `session_id`
- index on `event_type`
- index on `created_at`

---

## 15. `merge_events`

### Current role

Stores child merge history into parent nodes.

### Additional fields or rules to consider

- `merge_status text`
- `merge_base_sha text`

### Important constraints

- unique `(parent_node_version_id, child_node_version_id, merge_order, created_at)` may not be sufficient alone; exact uniqueness strategy needs design

### Important indexes

- index on `parent_node_version_id`
- index on `child_node_version_id`
- composite index on `(parent_node_version_id, merge_order)`

### Application-enforced rules

- merge order should match deterministic ordering policy

---

## 16. `merge_conflicts`

### Current role

Stores conflict metadata for merge events.

### Additional fields or rules to consider

- constrain `resolution_status`

### Important indexes

- index on `merge_event_id`
- index on `resolution_status`

---

## 17. `rebuild_events`

### Current role

Stores supersession/rebuild transitions.

### Additional fields or rules to consider

- `rebuild_scope text` such as self-only, subtree, upstream

### Important constraints

- old and new node IDs must differ

### Important indexes

- index on `old_node_version_id`
- index on `new_node_version_id`
- index on `created_at`

---

## 18. `prompts`

### Current role

Stores prompt history associated with runs and subtasks.

### Additional fields or rules to consider

- constrain `prompt_role`
- `prompt_kind text`

### Important indexes

- index on `node_run_id`
- index on `compiled_subtask_id`
- index on `prompt_role`
- index on `content_hash`

---

## 19. `summaries`

### Current role

Stores summaries for node versions and/or runs.

### Additional fields or rules to consider

- constrain `summary_type`
- `summary_scope text` such as subtask, node, failure, review, rectify

### Important indexes

- index on `node_version_id`
- index on `node_run_id`
- index on `summary_type`
- index on `created_at`

---

## 20. `node_docs`

### Current role

Stores generated documentation views.

### Additional fields or rules to consider

- `doc_status text`
- `generator_version text`

### Important constraints

- `view_scope` already bounded conceptually
- consider uniqueness on `(node_version_id, view_scope, doc_kind, path, content_hash)`

### Important indexes

- index on `node_version_id`
- index on `view_scope`
- index on `doc_kind`
- index on `content_hash`

---

## 21. `code_entities`

### Current role

Stores normalized code entities used for provenance and docs.

### Additional fields or rules to consider

- constrain `entity_type`
- `language text`
- `repository_path text`

### Important constraints

- uniqueness strategy needs careful design; likely some combination of entity type, canonical name, file path, signature, and stable hash

### Important indexes

- index on `entity_type`
- index on `canonical_name`
- index on `file_path`
- index on `stable_hash`

### Application-enforced rules

- stable identity across refactors may require matching heuristics beyond SQL

---

## 22. `node_entity_changes`

### Current role

Links node versions to entity changes and rationale.

### Additional fields or rules to consider

- constrain `change_type`
- `confidence numeric`

### Important constraints

- consider uniqueness on `(node_version_id, entity_id, change_type)`

### Important indexes

- index on `node_version_id`
- index on `entity_id`
- index on `change_type`

---

## 23. `code_relations`

### Current role

Stores relationships between code entities.

### Additional fields or rules to consider

- constrain `relation_type`
- constrain `source`

### Important constraints

- prevent self-relations unless explicitly allowed

### Important indexes

- index on `from_entity_id`
- index on `to_entity_id`
- index on `relation_type`
- index on `source`

---

## Missing Result Tables To Consider

The current spec may need additional dedicated tables for quality systems rather than overloading summaries.

### 1. `validation_results`

Possible purpose:

- persist validation executions at node/run/subtask granularity
- track pass/fail status per check
- support CLI review of validation history

### 2. `review_results`

Possible purpose:

- persist review outputs, recommendations, decision status, and review scope

### 3. `test_results`

Possible purpose:

- persist testing executions, suite names, pass/fail counts, retries, and failure summaries

### 4. `workflow_events`

Canonical purpose:

- append-only event log for major workflow transitions that are not reconstructible cleanly from current state plus attempts

Examples:

- pause entered/cleared/resumed
- recovery attempted/succeeded/failed
- parent decision events
- cutover completed
- lineage superseded

---

## Recommended Views To Add

The existing views are useful, but more current-state views likely belong in v2.

### `active_primary_sessions`

Purpose:

- surface the currently active primary session for each node run

### `current_node_cursors`

Purpose:

- flatten node, run, workflow, task, and current subtask into one operational query surface

### `pending_dependency_nodes`

Purpose:

- show which nodes are blocked and on what dependencies

### `latest_validation_results`

Purpose:

- expose current validation status by node/run/subtask

### `latest_review_results`

Purpose:

- expose current review status by node/run/subtask

### `latest_test_results`

Purpose:

- expose current testing status by node/run/subtask

### `latest_pause_state`

Purpose:

- expose current gating and pause reasons without reconstructing event history manually

### `authoritative_node_versions`

Purpose:

- expose the current effective authoritative version per logical node

### `candidate_node_versions`

Purpose:

- expose newer durable versions that are latest-created but not yet authoritative

### `latest_parent_child_authority`

Purpose:

- expose current child authority mode and layout hash for each parent node version

### `candidate_lineage_edges`

Purpose:

- expose candidate rebuild lineage separately from authoritative tree edges

---

## Recommended Indexing Priorities

If indexes need to be phased, these are likely highest value.

### Priority 1: runtime path indexes

- current node run lookup
- current node cursor lookup
- current compiled subtask lookup
- active primary session lookup
- dependency blocker lookup

### Priority 2: CLI/operator path indexes

- subtree traversal
- lineage traversal
- merge history lookup
- summary history lookup
- prompt history lookup

### Priority 3: provenance/docs path indexes

- entity by canonical name
- entity history lookup
- relation lookup
- node docs lookup

---

## Integrity Rules SQL Likely Cannot Fully Enforce

Some important rules are not easily expressible purely with SQL constraints and should be listed explicitly as application-enforced invariants.

### Hierarchy invariants

- no cycles in node trees
- dependency edges only between allowed relatives
- child tier/kind must match parent constraints

### Runtime invariants

- only one active run per node version
- only one active primary session per active run
- current task/subtask must belong to the run's compiled workflow
- cursor advancement must follow compiled dependency graph
- authoritative dependency resolution must use authoritative lineage, not merely the latest-created candidate lineage

### Rebuild invariants

- supersession cutover happens only after the new lineage is stable
- merge order follows deterministic policy
- rectification reuses current sibling finals correctly

### Provenance invariants

- entity identity resolution across refactors may require heuristics
- rationale attachment may be probabilistic or confidence-based

---

## Highest-Priority Database Gaps

The biggest current DB-spec gaps appear to be:

1. explicit constrained value catalogs for statuses and types
2. dedicated result tables for validation, review, and testing
3. stronger session-role and session-parent modeling
4. clearer current-state uniqueness rules
5. stronger indexing plan for runtime and CLI queries
6. stronger provenance identity rules
7. explicit pause/event audit structures if needed

---

## Recommended Next DB Follow-On Work

The next DB-focused documents or actions should be:

1. write `notes/planning/expansion/runtime_pseudocode_plan.md`
2. use that pseudocode to confirm missing DB state
3. draft `notes/specs/database/database_schema_spec_v2.md`
4. optionally write a dedicated `notes/catalogs/vocabulary/state_value_catalog.md` for bounded statuses/types

---

## Exit Criteria

This DB expansion pass should be considered complete when:

- every major durable entity is accounted for
- key constraints are identified
- key indexes are identified
- bounded value catalogs are identified
- application-enforced invariants are listed explicitly
- missing result/event tables are called out clearly

At that point, the database design is concrete enough to draft the canonical v2 schema spec.
