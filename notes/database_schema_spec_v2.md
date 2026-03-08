# Database Schema Spec V2

## Purpose

This document defines the canonical database model for hierarchy, execution, compilation, git lineage, quality gates, documentation, and provenance.

V2 expands the prior database design by:

- clarifying the database as the durable canonical record for orchestration state
- tightening value-model and constraint expectations
- adding explicit persistence expectations for review and testing
- clarifying session and recovery modeling
- identifying additional views needed for runtime and operator introspection

PostgreSQL is assumed.

---

## 1. Core design rules

1. store node hierarchy durably
2. version nodes instead of mutating them in place
3. support configurable tiers and kinds rather than a hardcoded ladder
4. compile source YAML into immutable workflow snapshots
5. persist compiled tasks, subtasks, checks, and dependencies
6. persist run cursors and subtask-attempt history durably
7. persist session lineage and recovery-critical session state
8. persist git lineage, merge events, conflict events, and rebuild events
9. persist quality-gate results for validation, review, and testing
10. persist prompt, summary, docs, and provenance views
11. expose operationally relevant durable state through CLI

No critical orchestration state should exist only in memory if it affects execution, recovery, auditability, or operator decisions.

The database is not the live coordination authority.

Recommended model:

- the daemon owns live orchestration decisions
- the database stores the durable canonical record needed for recovery, auditability, and operator inspection

---

## 2. Value-model guidance

The schema may still use `text` in examples for readability, but V2 expects bounded operational values to be constrained through one of:

- PostgreSQL enum
- domain
- `text` with `check` constraint

Candidates include:

- node lifecycle state
- node run status
- dependency type
- session role
- session status
- summary type
- prompt role
- subtask type
- validation check type
- review status
- test status
- merge conflict resolution status

JSON should be used only where the shape is intentionally extensible rather than obviously relational.

---

## 3. Core hierarchy tables

### `logical_node_current_versions`

```sql
create table logical_node_current_versions (
  logical_node_id uuid primary key,
  authoritative_node_version_id uuid not null references node_versions(id),
  latest_created_node_version_id uuid not null references node_versions(id),
  updated_at timestamptz not null default now()
);
```

Purpose:

- separate immutable node-version history from current-version selection
- support conservative cutover where a candidate rebuilt lineage exists but is not yet authoritative
- expose the latest created version independently from the current effective version

Recommended indexes:

- `(authoritative_node_version_id)`
- `(latest_created_node_version_id)`

Application-enforced invariants:

- both referenced versions must belong to the same `logical_node_id`
- dependency resolution and default current-state views must use `authoritative_node_version_id`

### `node_versions`

```sql
create table node_versions (
  id uuid primary key,
  logical_node_id uuid not null,
  parent_node_version_id uuid references node_versions(id),
  tier text not null,
  node_kind text not null,
  title text not null,
  description text,
  status text not null,
  version_number integer not null,
  supersedes_node_version_id uuid references node_versions(id),
  active_branch_name text,
  branch_generation_number integer,
  seed_commit_sha text,
  final_commit_sha text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(logical_node_id, version_number),
  unique(supersedes_node_version_id),
  check (version_number > 0),
  check (supersedes_node_version_id is null or supersedes_node_version_id <> id)
);
```

Purpose:

- separate logical node identity from version identity
- support supersession and historical lineage
- store branch and git lineage metadata

Recommended indexes:

- `(logical_node_id)`
- `(parent_node_version_id)`
- `(status)`
- `(supersedes_node_version_id)`
- `(active_branch_name)`

Application-enforced invariants:

- only one authoritative version per logical node through `logical_node_current_versions`
- no cycles in the node tree

### `node_children`

```sql
create table node_children (
  parent_node_version_id uuid not null references node_versions(id),
  child_node_version_id uuid not null references node_versions(id),
  origin_type text not null default 'layout_generated',
  ordinal integer,
  created_at timestamptz not null default now(),
  primary key (parent_node_version_id, child_node_version_id),
  check (parent_node_version_id <> child_node_version_id),
  check (origin_type in ('manual','layout_generated','layout_generated_then_modified'))
);
```

Recommended indexes:

- `(parent_node_version_id)`
- `(child_node_version_id)`
- `(parent_node_version_id, ordinal)`

Application-enforced invariants:

- each child version has at most one parent
- parent/child kind and tier relationships must satisfy YAML constraints

### `parent_child_authority`

```sql
create table parent_child_authority (
  parent_node_version_id uuid primary key references node_versions(id),
  authority_mode text not null check (authority_mode in ('manual','layout_authoritative','hybrid')),
  authoritative_layout_hash text,
  last_reconciled_at timestamptz,
  updated_at timestamptz not null default now()
);
```

Purpose:

- persist whether a parent's child set is manual, layout-authoritative, or hybrid
- support explicit reconciliation for mixed manual/layout trees
- prevent silent structural rematerialization when layout authority is no longer exclusive

---

## 4. Dependency tables

### `node_dependencies`

```sql
create table node_dependencies (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  depends_on_node_version_id uuid not null references node_versions(id),
  dependency_type text not null check (dependency_type in ('child','sibling')),
  required_state text not null default 'COMPLETE',
  created_at timestamptz not null default now(),
  unique(node_version_id, depends_on_node_version_id),
  check (node_version_id <> depends_on_node_version_id)
);
```

Recommended indexes:

- `(node_version_id)`
- `(depends_on_node_version_id)`
- `(node_version_id, required_state)`

Application-enforced invariants:

- dependency targets may only be valid siblings or children
- parent/cousin/nibling dependencies are not allowed

Dependencies must be enforced in run admission and cursor advancement.

### `node_version_lineage`

```sql
create table node_version_lineage (
  parent_node_version_id uuid not null references node_versions(id),
  child_node_version_id uuid not null references node_versions(id),
  lineage_scope text not null check (lineage_scope in ('authoritative','candidate')),
  created_at timestamptz not null default now(),
  primary key (parent_node_version_id, child_node_version_id, lineage_scope),
  check (parent_node_version_id <> child_node_version_id)
);
```

Purpose:

- represent candidate rebuild lineages separately from authoritative lineage
- let rectification build a candidate parent/child chain before cutover
- avoid overloading `parent_node_version_id` on `node_versions` as the only lineage relationship during rebuilds

Recommended indexes:

- `(parent_node_version_id, lineage_scope)`
- `(child_node_version_id, lineage_scope)`

---

## 5. Source and compilation tables

### `source_documents`

```sql
create table source_documents (
  id uuid primary key,
  doc_family text not null,
  path text not null,
  source_scope text not null,
  content text not null,
  content_hash text not null,
  merge_mode text not null,
  created_at timestamptz not null default now(),
  unique(path, content_hash)
);
```

Purpose:

- store built-in, extension, and override source documents used during compilation

Recommended indexes:

- `(doc_family)`
- `(path)`
- `(content_hash)`
- `(source_scope)`

### `compiled_workflows`

```sql
create table compiled_workflows (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  source_hash text not null,
  resolved_yaml jsonb not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(source_hash)`
- `(created_at)`

### `compiled_workflow_sources`

```sql
create table compiled_workflow_sources (
  compiled_workflow_id uuid not null references compiled_workflows(id),
  source_document_id uuid not null references source_documents(id),
  source_role text not null,
  primary key (compiled_workflow_id, source_document_id)
);
```

Purpose:

- preserve exact source lineage for each compiled workflow

Recommended indexes:

- `(source_document_id)`
- `(source_role)`

---

## 6. Compiled task and subtask tables

### `compiled_tasks`

```sql
create table compiled_tasks (
  id uuid primary key,
  compiled_workflow_id uuid not null references compiled_workflows(id),
  task_key text not null,
  ordinal integer not null,
  title text,
  description text,
  config_json jsonb,
  created_at timestamptz not null default now(),
  unique(compiled_workflow_id, task_key),
  unique(compiled_workflow_id, ordinal)
);
```

Recommended indexes:

- `(compiled_workflow_id)`
- `(compiled_workflow_id, ordinal)`

### `compiled_subtasks`

```sql
create table compiled_subtasks (
  id uuid primary key,
  compiled_workflow_id uuid not null references compiled_workflows(id),
  compiled_task_id uuid not null references compiled_tasks(id),
  source_subtask_key text not null,
  ordinal integer not null,
  subtask_type text not null,
  title text,
  prompt_text text,
  command_text text,
  args_json jsonb,
  env_json jsonb,
  retry_policy_json jsonb,
  block_on_user_flag text,
  pause_summary_prompt text,
  inserted_by_hook boolean not null default false,
  inserted_by_hook_id uuid,
  source_file_path text,
  source_hash text,
  created_at timestamptz not null default now(),
  unique(compiled_task_id, ordinal)
);
```

Recommended indexes:

- `(compiled_workflow_id)`
- `(compiled_task_id)`
- `(subtask_type)`
- `(compiled_task_id, ordinal)`

### `compiled_subtask_dependencies`

```sql
create table compiled_subtask_dependencies (
  compiled_subtask_id uuid not null references compiled_subtasks(id),
  depends_on_compiled_subtask_id uuid not null references compiled_subtasks(id),
  primary key (compiled_subtask_id, depends_on_compiled_subtask_id),
  check (compiled_subtask_id <> depends_on_compiled_subtask_id)
);
```

Recommended indexes:

- `(compiled_subtask_id)`
- `(depends_on_compiled_subtask_id)`

### `compiled_subtask_checks`

```sql
create table compiled_subtask_checks (
  id uuid primary key,
  compiled_subtask_id uuid not null references compiled_subtasks(id),
  ordinal integer not null,
  check_type text not null,
  config_json jsonb not null,
  created_at timestamptz not null default now(),
  unique(compiled_subtask_id, ordinal)
);
```

Recommended indexes:

- `(compiled_subtask_id)`
- `(check_type)`

---

## 7. Execution tables

### `node_runs`

```sql
create table node_runs (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  run_number integer not null,
  trigger_reason text not null,
  run_status text not null,
  compiled_workflow_id uuid not null references compiled_workflows(id),
  started_at timestamptz,
  ended_at timestamptz,
  summary text,
  unique(node_version_id, run_number),
  check (run_number > 0)
);
```

Recommended indexes:

- `(node_version_id)`
- `(compiled_workflow_id)`
- `(run_status)`
- `(node_version_id, run_number desc)`

Application-enforced invariants:

- only one active run per node version unless the system intentionally supports more
- current primary-session identity should be derived from `sessions`, not duplicated on `node_runs`

### `node_run_state`

```sql
create table node_run_state (
  node_run_id uuid primary key references node_runs(id),
  lifecycle_state text not null,
  current_task_id uuid references compiled_tasks(id),
  current_compiled_subtask_id uuid references compiled_subtasks(id),
  current_subtask_attempt integer,
  last_completed_compiled_subtask_id uuid references compiled_subtasks(id),
  execution_cursor_json jsonb,
  failure_count_from_children integer not null default 0,
  failure_count_consecutive integer not null default 0,
  defer_to_user_threshold integer,
  pause_flag_name text,
  is_resumable boolean not null default true,
  working_tree_state text,
  updated_at timestamptz not null default now(),
  check (failure_count_from_children >= 0),
  check (failure_count_consecutive >= 0),
  check (current_subtask_attempt is null or current_subtask_attempt > 0)
);
```

Recommended indexes:

- `(lifecycle_state)`
- `(current_task_id)`
- `(current_compiled_subtask_id)`
- `(pause_flag_name)`

Application-enforced invariants:

- task and subtask pointers must belong to the run's compiled workflow
- cursor advancement must respect compiled dependency readiness

### `node_run_child_failure_counters`

This structure is canonical for per-child failure thresholds and parent decision history.

```sql
create table node_run_child_failure_counters (
  node_run_id uuid not null references node_runs(id),
  child_node_version_id uuid not null references node_versions(id),
  failure_count integer not null default 0,
  last_failure_at timestamptz,
  last_failure_class text,
  updated_at timestamptz not null default now(),
  primary key (node_run_id, child_node_version_id),
  check (failure_count >= 0)
);
```

Recommended indexes:

- `(child_node_version_id)`
- `(node_run_id, failure_count desc)`
- `(last_failure_class)`

Application-enforced invariants:

- child rows must refer only to node versions that are children of the run's node version in the authoritative lineage for that run
- the row is incremented durably before the parent chooses retry, regenerate, replan, or pause
- total and consecutive counters on `node_run_state` remain the current aggregate view, while this table provides the per-child durable detail

### `subtask_attempts`

```sql
create table subtask_attempts (
  id uuid primary key,
  node_run_id uuid not null references node_runs(id),
  compiled_subtask_id uuid not null references compiled_subtasks(id),
  attempt_number integer not null,
  status text not null,
  input_context_json jsonb,
  output_json jsonb,
  changed_files_json jsonb,
  git_head_before text,
  git_head_after text,
  validation_json jsonb,
  summary text,
  started_at timestamptz,
  ended_at timestamptz,
  unique(node_run_id, compiled_subtask_id, attempt_number),
  check (attempt_number > 0)
);
```

Recommended indexes:

- `(node_run_id)`
- `(compiled_subtask_id)`
- `(status)`
- `(node_run_id, compiled_subtask_id, attempt_number desc)`

---

## 8. Quality-gate result tables

V2 recommends dedicated persistence for validation, review, and testing rather than relying only on summaries.

### `validation_results`

```sql
create table validation_results (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  node_run_id uuid references node_runs(id),
  compiled_subtask_id uuid references compiled_subtasks(id),
  check_type text not null,
  status text not null,
  evidence_json jsonb,
  summary text,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(compiled_subtask_id)`
- `(status)`

### `review_results`

```sql
create table review_results (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  node_run_id uuid references node_runs(id),
  compiled_subtask_id uuid references compiled_subtasks(id),
  review_definition_id text,
  scope text not null,
  status text not null,
  criteria_json jsonb,
  findings_json jsonb,
  summary text,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(compiled_subtask_id)`
- `(status)`
- `(scope)`

### `test_results`

```sql
create table test_results (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  node_run_id uuid references node_runs(id),
  compiled_subtask_id uuid references compiled_subtasks(id),
  testing_definition_id text,
  suite_name text,
  status text not null,
  attempt_number integer,
  results_json jsonb,
  summary text,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(compiled_subtask_id)`
- `(status)`
- `(suite_name)`

### `compile_failures`

```sql
create table compile_failures (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  failure_stage text not null,
  failure_class text not null,
  summary text not null,
  details_json jsonb,
  source_hash text,
  target_family text,
  target_id text,
  hook_id text,
  policy_id text,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(failure_stage)`
- `(failure_class)`
- `(created_at)`

---

## 9. Prompt, summary, and docs tables

### `prompts`

```sql
create table prompts (
  id uuid primary key,
  node_run_id uuid not null references node_runs(id),
  compiled_subtask_id uuid references compiled_subtasks(id),
  prompt_role text not null,
  content text not null,
  content_hash text not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_run_id)`
- `(compiled_subtask_id)`
- `(prompt_role)`
- `(content_hash)`

### `summaries`

```sql
create table summaries (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  node_run_id uuid references node_runs(id),
  summary_type text not null,
  content text not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(summary_type)`
- `(created_at)`

### `node_docs`

```sql
create table node_docs (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  view_scope text not null check (view_scope in ('local','merged')),
  doc_kind text not null,
  path text not null,
  content text not null,
  content_hash text not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(view_scope)`
- `(doc_kind)`
- `(content_hash)`

Possible future addition:

- a dedicated docs build-event table if docs generation requires richer operational history

---

## 10. Sessions and runtime tables

### `sessions`

```sql
create table sessions (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  node_run_id uuid references node_runs(id),
  session_role text not null,
  parent_session_id uuid references sessions(id),
  provider text not null,
  provider_session_id text,
  tmux_session_name text,
  cwd text,
  status text not null,
  started_at timestamptz not null default now(),
  last_heartbeat_at timestamptz,
  ended_at timestamptz,
  check (
    (session_role = 'primary' and parent_session_id is null) or
    (session_role = 'pushed_child' and parent_session_id is not null)
  )
);
```

Purpose:

- support primary node sessions and optional pushed child sessions

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(session_role)`
- `(provider_session_id)`
- `(tmux_session_name)`
- `(status)`
- `(parent_session_id)`

Application-enforced invariants:

- only one active primary session per active run
- pushed child sessions do not own git state or workflow cursor ownership

### `session_events`

```sql
create table session_events (
  id uuid primary key,
  session_id uuid not null references sessions(id),
  event_type text not null,
  payload_json jsonb,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(session_id)`
- `(event_type)`
- `(created_at)`

### `child_session_results`

This structure is canonical for the pushed-child-session model.

```sql
create table child_session_results (
  id uuid primary key,
  child_session_id uuid not null references sessions(id),
  parent_compiled_subtask_id uuid references compiled_subtasks(id),
  status text not null,
  result_json jsonb not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(child_session_id)`
- `(parent_compiled_subtask_id)`
- `(status)`

---

## 11. Git lineage tables

### `merge_events`

```sql
create table merge_events (
  id uuid primary key,
  parent_node_version_id uuid not null references node_versions(id),
  child_node_version_id uuid not null references node_versions(id),
  child_final_commit_sha text not null,
  parent_commit_before text not null,
  parent_commit_after text not null,
  merge_order integer not null,
  had_conflict boolean not null default false,
  created_at timestamptz not null default now(),
  check (merge_order > 0)
);
```

Recommended indexes:

- `(parent_node_version_id)`
- `(child_node_version_id)`
- `(parent_node_version_id, merge_order)`

### `merge_conflicts`

```sql
create table merge_conflicts (
  id uuid primary key,
  merge_event_id uuid not null references merge_events(id),
  files_json jsonb not null,
  merge_base_sha text,
  resolution_summary text,
  resolution_status text not null,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(merge_event_id)`
- `(resolution_status)`

### `rebuild_events`

```sql
create table rebuild_events (
  id uuid primary key,
  old_node_version_id uuid not null references node_versions(id),
  new_node_version_id uuid not null references node_versions(id),
  trigger_reason text not null,
  trigger_payload_json jsonb,
  created_at timestamptz not null default now(),
  check (old_node_version_id <> new_node_version_id)
);
```

Recommended indexes:

- `(old_node_version_id)`
- `(new_node_version_id)`
- `(created_at)`

### `workflow_events`

This table is canonical and should remain intentionally narrow and focused on orchestration transitions that are not already well covered by subtask attempts or session events.

```sql
create table workflow_events (
  id uuid primary key,
  node_version_id uuid references node_versions(id),
  node_run_id uuid references node_runs(id),
  event_type text not null,
  event_scope text not null,
  payload_json jsonb,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(event_type)`
- `(event_scope)`
- `(created_at)`

Recommended event families:

- pause entered/cleared/resumed
- recovery attempted/succeeded/failed
- replacement session created
- parent decision events
- cutover completed
- lineage superseded

---

## 12. Provenance tables

### `code_entities`

```sql
create table code_entities (
  id uuid primary key,
  entity_type text not null,
  canonical_name text not null,
  file_path text,
  signature text,
  start_line integer,
  end_line integer,
  stable_hash text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Recommended indexes:

- `(entity_type)`
- `(canonical_name)`
- `(file_path)`
- `(stable_hash)`

Application-enforced invariants:

- stable identity across refactors may require heuristic matching beyond pure SQL constraints

### `node_entity_changes`

```sql
create table node_entity_changes (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  entity_id uuid not null references code_entities(id),
  change_type text not null,
  rationale_summary text,
  created_at timestamptz not null default now()
);
```

Recommended indexes:

- `(node_version_id)`
- `(entity_id)`
- `(change_type)`

### `code_relations`

```sql
create table code_relations (
  id uuid primary key,
  from_entity_id uuid not null references code_entities(id),
  to_entity_id uuid not null references code_entities(id),
  relation_type text not null,
  source text not null,
  confidence numeric,
  created_at timestamptz not null default now(),
  check (from_entity_id <> to_entity_id)
);
```

Recommended indexes:

- `(from_entity_id)`
- `(to_entity_id)`
- `(relation_type)`
- `(source)`

---

## 13. Recommended views

### `active_node_versions`

```sql
create view active_node_versions as
select nv.*
from node_versions nv
join logical_node_current_versions lcv
  on lcv.authoritative_node_version_id = nv.id;
```

### `latest_node_runs`

```sql
create view latest_node_runs as
select distinct on (node_version_id)
  *
from node_runs
order by node_version_id, run_number desc;
```

### `latest_subtask_attempts`

```sql
create view latest_subtask_attempts as
select distinct on (node_run_id, compiled_subtask_id)
  *
from subtask_attempts
order by node_run_id, compiled_subtask_id, attempt_number desc;
```

### Additional recommended current-state views

#### `active_primary_sessions`

Purpose:

- expose the current primary session for each active run

Recommended implementation:

- derive from `sessions`
- filter to `session_role = 'primary'`
- filter to active statuses
- do not treat `node_runs` as the canonical owner of session identity

#### `current_node_cursors`

Purpose:

- flatten node, run, workflow, task, and current subtask into one operational surface

#### `pending_dependency_nodes`

Purpose:

- show which nodes are blocked and on what dependencies

#### `latest_validation_results`

Purpose:

- expose latest validation state by node/run/subtask

#### `latest_review_results`

Purpose:

- expose latest review state by node/run/subtask

#### `latest_test_results`

Purpose:

- expose latest testing state by node/run/subtask

#### `authoritative_node_versions`

Purpose:

- expose the current effective authoritative version for each logical node when candidate superseding lineages exist

Recommended implementation:

- derive directly from `logical_node_current_versions.authoritative_node_version_id`

#### `candidate_node_versions`

Purpose:

- expose newer superseding versions that are durable and queryable but not yet authoritative pending cutover

Recommended implementation:

- derive from `logical_node_current_versions.latest_created_node_version_id`
- exclude versions already selected as authoritative

#### `latest_parent_child_authority`

Purpose:

- expose the current child authority mode and authoritative layout hash for each parent node version

#### `candidate_lineage_edges`

Purpose:

- expose candidate rebuild lineage separately from authoritative lineage

---

## 14. Example queries for basic operations

### A. Dump full subtree from a node

```sql
with recursive subtree as (
  select id, parent_node_version_id, title, node_kind, tier, 0 as depth
  from node_versions
  where id = $1

  union all

  select nv.id, nv.parent_node_version_id, nv.title, nv.node_kind, nv.tier, st.depth + 1
  from node_versions nv
  join subtree st on nv.parent_node_version_id = st.id
)
select *
from subtree
order by depth, title;
```

### B. Walk from a node to the top node

```sql
with recursive ancestors as (
  select id, parent_node_version_id, title, node_kind, tier, 0 as depth
  from node_versions
  where id = $1

  union all

  select nv.id, nv.parent_node_version_id, nv.title, nv.node_kind, nv.tier, a.depth + 1
  from node_versions nv
  join ancestors a on a.parent_node_version_id = nv.id
)
select *
from ancestors
order by depth;
```

### C. Show active run cursor for a node

```sql
select
  nr.id as node_run_id,
  nrs.lifecycle_state,
  nrs.current_task_id,
  nrs.current_compiled_subtask_id,
  nrs.current_subtask_attempt,
  nrs.last_completed_compiled_subtask_id,
  nrs.pause_flag_name
from latest_node_runs nr
join node_run_state nrs on nrs.node_run_id = nr.id
where nr.node_version_id = $1;
```

---

## 15. Application-enforced invariants

Some critical rules are difficult to express purely with SQL and must be enforced by application/runtime logic.

### Hierarchy invariants

- no cycles in the node tree
- child kinds/tiers must satisfy parent constraints
- dependency edges only point to allowed relatives

### Runtime invariants

- only one active run per node version unless intentionally allowed
- only one active primary session per active run
- current task and subtask pointers belong to the run's compiled workflow
- cursor advancement respects subtask dependency graph
- coordination-critical mutations are validated by daemon logic before durable acceptance

### Rebuild invariants

- supersession cutover happens only after the new lineage is stable
- merge order follows deterministic policy
- upstream rectification uses current sibling finals appropriately
- authoritative and candidate lineage views must not be conflated during rebuild
- `logical_node_current_versions` must be the canonical selector for authoritative versus latest-created versions
- `sessions` must be the canonical owner of current session identity for runs

### Provenance invariants

- entity identity across refactors may require heuristic matching
- rationale linkage may involve confidence or post-processing

---

## 16. V2 closure notes

This V2 DB spec resolves or reduces the following prior gaps:

- stronger persistence model for review/testing
- stronger session-role modeling
- clearer index and constraint expectations
- more explicit current-state and history query surfaces

Remaining follow-on work still needed:

- freeze bounded value catalogs in migration-grade form
- decide whether docs build events need a dedicated table
- define the exact SQL or materialized-view implementation for authoritative-versus-candidate lineage read surfaces
- define whether `parent_child_authority` needs a history table in addition to current-state storage
- align runtime, lifecycle, CLI, and git v2 specs to these structures
