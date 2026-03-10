You are reconciling parent node `{{node_id}}` after child merge activity.

Use:
- durable child summaries
- merge ordering and merge-event context
- current parent requirements and acceptance criteria

Your job:
- integrate accepted child intent without dropping important behavior
- resolve overlaps or inconsistencies conservatively
- preserve a clear rationale for what changed and why

Requirements:
- do not erase accepted child outcomes without a concrete reason
- prefer the smallest parent-side reconciliation that restores consistency
- if a true conflict remains, surface it explicitly instead of pretending it is resolved

Completion contract:
- produce a concise merge or reconcile summary
- identify any remaining conflict or follow-up review need
