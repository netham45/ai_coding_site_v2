# Automation Of All User-Visible Actions Decisions

## Scope implemented in this slice

- Added durable cancel automation for active node runs through `node cancel` and `workflow cancel`.
- Added durable subtask retry automation through `subtask retry --node ...` and `subtask retry --attempt ...`.
- Added the top-level `rebuild show --node ...` alias for rebuild-history inspection.
- Tightened CLI and test-client error handling so daemon `404` and `409` responses become structured CLI failures instead of opaque payloads.

## Key implementation decisions

- Cancellation remains a daemon authority mutation first, with run-orchestration cleanup layered on top, so the audit trail is split across daemon mutation events and `workflow_events`.
- Retry remains bounded to the latest retryable run for the targeted compiled subtask rather than creating an all-new run lineage.
- `subtask retry --attempt ...` is defined as a convenience lookup over the owning run/subtask, not as a separate retry policy with independent lifecycle semantics.
- The in-process `DaemonBridgeClient` test helper now mirrors the production CLI daemon client for error translation so CLI round-trip tests exercise the same failure semantics as the shipped path.
- The `0023` Alembic revision id was shortened to `0023_action_automation` to stay within the repository's current `alembic_version.version_num` length limit.

## Deferred work

- Layout authoring/update automation still needs concrete mutation commands and durable artifact semantics.
- Policy-update automation still remains outside this slice.
- Cancellation is intentionally bounded to active runs; broader administrative force-stop semantics remain deferred.
