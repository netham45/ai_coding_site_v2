# Frontend Website UI Expanded Tree Contract

## Purpose

Propose the expanded browser-facing tree response for the website sidebar and explorer shell.

This is a working note, not an implementation plan.

## Recommendation

Keep the existing tree route and expand it.

Suggested route:

- `GET /api/nodes/{node_id}/tree`

Current recommendation:

- do not add a second browser-only tree endpoint

Why:

- the existing tree route already expresses the correct conceptual object
- the current operator-view loader already gathers much of the needed data
- expanding the existing response keeps CLI and website thinking aligned

## Current Backend Baseline

Current tree response already includes:

- `node_id`
- `parent_node_id`
- `depth`
- `kind`
- `tier`
- `title`
- `lifecycle_state`
- `run_status`
- `scheduling_status`
- `blocker_count`

The website needs a richer version of that same object, not a different concept.

## Proposed Response

```json
{
  "root_node_id": "node_100",
  "generated_at": "2026-03-11T12:00:00Z",
  "nodes": [
    {
      "node_id": "node_100",
      "parent_node_id": null,
      "depth": 0,
      "kind": "epic",
      "tier": "epic",
      "title": "Refactor daemon website operator UI",
      "authoritative_node_version_id": "nv_100",
      "latest_created_node_version_id": "nv_101",
      "lifecycle_state": "READY",
      "run_status": "RUNNING",
      "scheduling_status": "already_running",
      "blocker_count": 0,
      "blocker_state": "none",
      "has_children": true,
      "child_count": 3,
      "child_rollups": {
        "total": 3,
        "ready": 1,
        "running": 1,
        "paused_for_user": 0,
        "blocked": 0,
        "failed": 0,
        "complete": 1,
        "superseded": 0,
        "not_compiled": 0
      },
      "created_at": "2026-03-11T11:00:00Z",
      "last_updated_at": "2026-03-11T12:00:00Z"
    }
  ]
}
```

## Proposed Field Additions

### Version fields

- `authoritative_node_version_id`
- `latest_created_node_version_id`

Why:

- the UI needs to distinguish current authoritative state from newer created candidates

### Child-shape fields

- `has_children`
- `child_count`

Why:

- avoids extra follow-up requests just to know whether expansion affordances should appear

### Blocker summary fields

- `blocker_state`
- `blocker_count`

Why:

- the UI needs a quick status class, not just a raw count

Suggested `blocker_state` values:

- `none`
- `blocked`
- `paused_for_user`

### Child rollup field

- `child_rollups`

Why:

- the tree needs glanceable higher-level status summaries

Recommended scope:

- immediate children only, not whole descendant subtree

### Timestamp fields

- `created_at`
- `last_updated_at`

Why:

- the UI needs freshness and ordering context

## Suggested Rollup Vocabulary

Recommended child-rollup buckets:

- `total`
- `ready`
- `running`
- `paused_for_user`
- `blocked`
- `failed`
- `complete`
- `superseded`
- `not_compiled`

This vocabulary should track the daemon’s actual lifecycle and scheduling vocabulary as closely as possible.

## Derivation Guidance

### `authoritative_node_version_id`

Source:

- current version selector

### `latest_created_node_version_id`

Source:

- current version selector

### `child_count`

Source:

- direct child count from hierarchy edges

### `has_children`

Source:

- `child_count > 0`

### `blocker_count`

Source:

- dependency blockers for the authoritative version

### `blocker_state`

Source:

- derived from blocker count plus pause/lifecycle state

### `last_updated_at`

Recommended derivation:

- latest relevant timestamp from lifecycle, version selector, authoritative version, or related runtime records

The exact derivation should be frozen in implementation, but the frontend should only need one field.

## Why This Should Stay One Route

If the website does not get this data from one tree response, it will need to stitch together:

- tree
- summary
- lineage or versions
- blockers
- child counts

That will create more requests, more inconsistent refresh timing, and more frontend state complexity.

Expanding the existing route is the cleaner design.

## Frontend Expectations

The frontend should use this response for:

- sidebar rendering
- status badges
- child rollup indicators
- expand/collapse affordances
- selection context

The frontend should not use this response as a substitute for full node detail tabs.

## Related Notes

- `2026-03-11_v1_scope_freeze.md`
- `2026-03-11_review_and_expansion.md`
- `2026-03-11_information_architecture_and_routing.md`
