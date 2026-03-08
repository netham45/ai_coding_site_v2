# Manual Vs Auto Tree Reconciliation Flow

Source:

- `notes/manual_vs_auto_tree_interaction.md`

## Scenario

A parent originally materialized children from layout, then an operator manually adds a child.

## Full task flow

1. parent starts as layout-authoritative
2. operator manually creates `task_hotfix_v1`
3. parent authority mode becomes `hybrid`
4. a later layout update is requested
5. daemon detects hybrid structural authority
6. daemon pauses automatic structural rematerialization
7. parent must reconcile manual and layout authority explicitly

Simulated response:

```json
{
  "status": "PAUSE",
  "reason": "hybrid_tree_requires_reconciliation"
}
```

## Logic issues exposed

1. Child-origin and authority-mode fields are still not canonically represented in the DB model.

