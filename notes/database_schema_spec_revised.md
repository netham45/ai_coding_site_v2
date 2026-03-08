# Database Schema Spec

## Purpose

This document defines the database model for hierarchy, execution, compiled workflows, git lineage, documentation, and introspection.

The design goal is that no critical runner state is hidden only in memory. The database is the orchestration truth source, and all practical database operations should be exposable through CLI.

PostgreSQL is assumed.

---

## 1. Core design rules

1. store node hierarchy durably
2. version nodes instead of mutating them in place
3. support configurable tiers and node kinds rather than a hardcoded hierarchy
4. compile source YAML into immutable workflow snapshots
5. persist compiled subtasks with durable IDs
6. persist run cursors and prior subtask results
7. strictly enforce dependency readiness
8. persist git lineage and merge events
9. persist prompt, summary, and documentation views
10. expose everything through CLI query surfaces where sensible

---

## 2. Core hierarchy tables

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
  seed_commit_sha text,
  final_commit_sha text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(logical_node_id, version_number)
);
```

This separates logical identity from version identity and allows configurable hierarchy semantics through `tier` and `node_kind`.

### `node_children`

```sql
create table node_children (
  parent_node_version_id uuid not null references node_versions(id),
  child_node_version_id uuid not null references node_versions(id),
  ordinal integer,
  primary key (parent_node_version_id, child_node_version_id)
);
```

---

## 3. Source and compilation tables

### `source_documents`

```sql
create table source_documents (
  id uuid primary key,
  doc_family text not null,
  path text not null,
  content text not null,
  content_hash text not null,
  merge_mode text not null,
  created_at timestamptz not null default now()
);
```

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

### `compiled_workflow_sources`

```sql
create table compiled_workflow_sources (
  compiled_workflow_id uuid not null references compiled_workflows(id),
  source_document_id uuid not null references source_documents(id),
  source_role text not null,
  primary key (compiled_workflow_id, source_document_id)
);
```

These tables preserve exactly which base files, overrides, and hooks produced a workflow snapshot.

---

## 4. Compiled task and subtask tables

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
  created_at timestamptz not null default now()
);
```

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
  created_at timestamptz not null default now()
);
```

### `compiled_subtask_dependencies`

```sql
create table compiled_subtask_dependencies (
  compiled_subtask_id uuid not null references compiled_subtasks(id),
  depends_on_compiled_subtask_id uuid not null references compiled_subtasks(id),
  primary key (compiled_subtask_id, depends_on_compiled_subtask_id)
);
```

### `compiled_subtask_checks`

```sql
create table compiled_subtask_checks (
  id uuid primary key,
  compiled_subtask_id uuid not null references compiled_subtasks(id),
  ordinal integer not null,
  check_type text not null,
  config_json jsonb not null
);
```

This is the key layer for durable introspection and compatibility across YAML changes.

---

## 5. Execution tables

### `node_runs`

```sql
create table node_runs (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  run_number integer not null,
  trigger_reason text not null,
  run_status text not null,
  compiled_workflow_id uuid not null references compiled_workflows(id),
  session_id uuid,
  started_at timestamptz,
  ended_at timestamptz,
  summary text,
  unique(node_version_id, run_number)
);
```

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
  updated_at timestamptz not null default now()
);
```

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
  unique(node_run_id, compiled_subtask_id, attempt_number)
);
```

The runtime cursor and subtask history are stored durably so the runner does not need to keep invisible in-memory state.

---

## 6. Dependency tables

### `node_dependencies`

```sql
create table node_dependencies (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  depends_on_node_version_id uuid not null references node_versions(id),
  dependency_type text not null check (dependency_type in ('child','sibling')),
  required_state text not null default 'COMPLETE',
  created_at timestamptz not null default now(),
  unique(node_version_id, depends_on_node_version_id)
);
```

Dependencies should be strictly enforced in runtime admission and cursor advancement. If required dependencies are unsatisfied, the node should not run and subtasks that require them should not advance.

---

## 7. Git lineage tables

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
  created_at timestamptz not null default now()
);
```

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

### `rebuild_events`

```sql
create table rebuild_events (
  id uuid primary key,
  old_node_version_id uuid not null references node_versions(id),
  new_node_version_id uuid not null references node_versions(id),
  trigger_reason text not null,
  trigger_payload_json jsonb,
  created_at timestamptz not null default now()
);
```

---

## 8. Prompt, summary, and docs tables

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

---

## 9. Sessions and runtime tables

### `sessions`

```sql
create table sessions (
  id uuid primary key,
  node_version_id uuid not null references node_versions(id),
  provider text not null,
  provider_session_id text,
  tmux_session_name text,
  cwd text,
  status text not null,
  started_at timestamptz not null default now(),
  last_heartbeat_at timestamptz,
  ended_at timestamptz
);
```

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

This supports primary node sessions and optional pushed child sessions used for context-only research/review work.

---

## 10. Code provenance tables

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

### `code_relations`

```sql
create table code_relations (
  id uuid primary key,
  from_entity_id uuid not null references code_entities(id),
  to_entity_id uuid not null references code_entities(id),
  relation_type text not null,
  source text not null,
  confidence numeric,
  created_at timestamptz not null default now()
);
```

---

## 11. Recommended views

Recommended current-state views:

### `active_node_versions`

```sql
create view active_node_versions as
select nv.*
from node_versions nv
where not exists (
  select 1
  from node_versions newer
  where newer.supersedes_node_version_id = nv.id
);
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

---

## 12. Example queries for basic operations

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

### B. Walk from a node to top node

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
  nrs.execution_cursor_json,
  nrs.pause_flag_name
from latest_node_runs nr
join node_run_state nrs on nrs.node_run_id = nr.id
where nr.node_version_id = $1;
```

### D. List compiled subtasks for a node in order

```sql
select
  ct.task_key,
  cs.id,
  cs.ordinal,
  cs.source_subtask_key,
  cs.subtask_type,
  cs.title,
  cs.inserted_by_hook,
  cs.block_on_user_flag
from compiled_workflows cw
join compiled_tasks ct on ct.compiled_workflow_id = cw.id
join compiled_subtasks cs on cs.compiled_task_id = ct.id
where cw.node_version_id = $1
order by ct.ordinal, cs.ordinal;
```

### E. Show subtask execution history for a node run

```sql
select
  sa.compiled_subtask_id,
  cs.ordinal,
  cs.title,
  sa.attempt_number,
  sa.status,
  sa.started_at,
  sa.ended_at,
  sa.summary
from subtask_attempts sa
join compiled_subtasks cs on cs.id = sa.compiled_subtask_id
where sa.node_run_id = $1
order by cs.ordinal, sa.attempt_number;
```

### F. Show merge lineage for a node

```sql
select
  me.id,
  me.parent_node_version_id,
  me.child_node_version_id,
  me.child_final_commit_sha,
  me.parent_commit_before,
  me.parent_commit_after,
  me.merge_order,
  me.had_conflict,
  me.created_at
from merge_events me
where me.parent_node_version_id = $1
order by me.created_at, me.merge_order;
```

### G. Show which node versions changed a code entity

```sql
select
  nec.node_version_id,
  nv.title,
  nv.node_kind,
  nv.tier,
  nec.change_type,
  nec.rationale_summary,
  nec.created_at
from node_entity_changes nec
join node_versions nv on nv.id = nec.node_version_id
join code_entities ce on ce.id = nec.entity_id
where ce.canonical_name = $1
order by nec.created_at desc;
```

---

## 13. Query strategy

Use three layers:

1. base normalized tables for truth
2. stable views for common current-state lookups
3. recursive queries for tree traversal and lineage walks

Do not try to materialize every possible tree shape ahead of time.

For the expected V1 scale, views plus recursive CTEs should be sufficient.

---

## 14. Index recommendations

At minimum:

- `node_versions(logical_node_id)`
- `node_versions(parent_node_version_id)`
- `node_versions(supersedes_node_version_id)`
- `node_runs(node_version_id)`
- `node_run_state(current_compiled_subtask_id)`
- `compiled_workflows(node_version_id)`
- `compiled_tasks(compiled_workflow_id, ordinal)`
- `compiled_subtasks(compiled_task_id, ordinal)`
- `subtask_attempts(node_run_id, compiled_subtask_id, attempt_number)`
- `node_dependencies(node_version_id)`
- `node_dependencies(depends_on_node_version_id)`
- `merge_events(parent_node_version_id)`
- `merge_events(child_node_version_id)`
- `node_docs(node_version_id, view_scope)`
- `node_entity_changes(node_version_id)`
- `node_entity_changes(entity_id)`
- `code_entities(canonical_name)`
- `sessions(node_version_id)`

---

## 15. Final rule

The database is authoritative for:

- hierarchy
- versions
- compiled workflow state
- execution cursor and history
- git lineage metadata
- prompt and summary provenance
- documentation views
- runtime/session state

Git stores code history. The database stores orchestration truth.

