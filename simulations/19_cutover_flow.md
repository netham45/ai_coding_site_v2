# Cutover Flow

Source:

- `notes/cutover_policy_note.md`

## Scenario

A candidate rebuilt lineage has completed successfully from changed child through parent.

## Full task flow

1. old lineage remains authoritative during candidate rebuild
2. candidate child completes
3. candidate parent completes
4. daemon verifies rebuilt upstream path is stable
5. daemon records cutover event
6. daemon marks candidate lineage authoritative
7. daemon marks old lineage superseded

Simulated cutover event:

```yaml
event_type: cutover_completed
payload:
  old_authoritative_parent: plan_v1
  new_authoritative_parent: plan_v2
  old_authoritative_child: task_greeting_v1
  new_authoritative_child: task_greeting_v2
  cutover_scope: upstream_lineage
```

## Logic issues exposed

1. “Latest created version” versus “authoritative version” still needs a fully frozen representation in views and CLI output.

