from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.git_conflicts import has_unresolved_merge_conflicts, record_merge_conflict_in_session, record_merge_event_in_session
from aicoding.daemon.live_git import _git, _git_output, _git_try, _repo_path, _require_branch_name
from aicoding.db.models import (
    IncrementalChildMergeState,
    LogicalNodeCurrentVersion,
    NodeLifecycleState,
    NodeRun,
    NodeRunState,
    NodeVersion,
    ParentIncrementalMergeLane,
)
from aicoding.db.session import query_session_scope, session_scope

RECONCILE_PROMPT_PATH = "execution/reconcile_parent_after_merge.md"


@dataclass(frozen=True, slots=True)
class IncrementalChildMergeStateSnapshot:
    id: UUID
    parent_node_version_id: UUID
    child_node_version_id: UUID
    child_final_commit_sha: str
    status: str
    applied_merge_order: int | None
    parent_commit_before: str | None
    parent_commit_after: str | None
    conflict_id: UUID | None

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "child_node_version_id": str(self.child_node_version_id),
            "child_final_commit_sha": self.child_final_commit_sha,
            "status": self.status,
            "applied_merge_order": self.applied_merge_order,
            "parent_commit_before": self.parent_commit_before,
            "parent_commit_after": self.parent_commit_after,
            "conflict_id": None if self.conflict_id is None else str(self.conflict_id),
        }


@dataclass(frozen=True, slots=True)
class ParentIncrementalMergeLaneSnapshot:
    parent_node_version_id: UUID
    status: str
    current_parent_head_commit_sha: str | None
    last_successful_merge_at: str | None
    blocked_reason: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_version_id": str(self.parent_node_version_id),
            "status": self.status,
            "current_parent_head_commit_sha": self.current_parent_head_commit_sha,
            "last_successful_merge_at": self.last_successful_merge_at,
            "blocked_reason": self.blocked_reason,
        }


@dataclass(frozen=True, slots=True)
class IncrementalParentMergeExecutionSnapshot:
    parent_node_version_id: UUID
    child_node_version_id: UUID
    status: str
    applied_merge_order: int | None
    parent_commit_before: str | None
    parent_commit_after: str | None
    conflict_id: UUID | None
    lane_status: str

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_version_id": str(self.parent_node_version_id),
            "child_node_version_id": str(self.child_node_version_id),
            "status": self.status,
            "applied_merge_order": self.applied_merge_order,
            "parent_commit_before": self.parent_commit_before,
            "parent_commit_after": self.parent_commit_after,
            "conflict_id": None if self.conflict_id is None else str(self.conflict_id),
            "lane_status": self.lane_status,
        }


def record_completed_child_for_incremental_merge(
    session_factory: sessionmaker[Session],
    *,
    child_node_version_id: UUID,
) -> IncrementalChildMergeStateSnapshot | None:
    with session_scope(session_factory) as session:
        snapshot = record_completed_child_for_incremental_merge_in_session(
            session,
            child_node_version_id=child_node_version_id,
        )
        session.flush()
        return snapshot


def record_completed_child_for_incremental_merge_in_session(
    session: Session,
    *,
    child_node_version_id: UUID,
) -> IncrementalChildMergeStateSnapshot | None:
    child_version = session.get(NodeVersion, child_node_version_id)
    if child_version is None:
        return None
    if child_version.parent_node_version_id is None:
        return None
    if child_version.final_commit_sha is None:
        return None

    child_selector = session.get(LogicalNodeCurrentVersion, child_version.logical_node_id)
    if child_selector is None or child_selector.authoritative_node_version_id != child_node_version_id:
        return None

    parent_version = session.get(NodeVersion, child_version.parent_node_version_id)
    if parent_version is None:
        return None
    parent_selector = session.get(LogicalNodeCurrentVersion, parent_version.logical_node_id)
    if parent_selector is None or parent_selector.authoritative_node_version_id != parent_version.id:
        return None

    lane = session.get(ParentIncrementalMergeLane, parent_version.id)
    if lane is None:
        lane = ParentIncrementalMergeLane(
            parent_node_version_id=parent_version.id,
            status="pending",
            current_parent_head_commit_sha=parent_version.final_commit_sha or parent_version.seed_commit_sha,
            blocked_reason=None,
        )
        session.add(lane)
    elif lane.status == "idle":
        lane.status = "pending"
        lane.current_parent_head_commit_sha = lane.current_parent_head_commit_sha or parent_version.final_commit_sha or parent_version.seed_commit_sha

    row = session.execute(
        select(IncrementalChildMergeState).where(
            IncrementalChildMergeState.parent_node_version_id == parent_version.id,
            IncrementalChildMergeState.child_node_version_id == child_node_version_id,
        )
    ).scalar_one_or_none()
    if row is None:
        row = IncrementalChildMergeState(
            id=uuid4(),
            parent_node_version_id=parent_version.id,
            child_node_version_id=child_node_version_id,
            child_final_commit_sha=child_version.final_commit_sha,
            status="completed_unmerged",
        )
        session.add(row)
        session.flush()
    elif row.status == "completed_unmerged" and row.child_final_commit_sha != child_version.final_commit_sha:
        row.child_final_commit_sha = child_version.final_commit_sha

    return _incremental_child_merge_state_snapshot(row)


def list_incremental_child_merge_states_for_parent(
    session_factory: sessionmaker[Session],
    *,
    parent_node_version_id: UUID,
) -> list[IncrementalChildMergeStateSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(IncrementalChildMergeState)
            .where(IncrementalChildMergeState.parent_node_version_id == parent_node_version_id)
            .order_by(IncrementalChildMergeState.created_at, IncrementalChildMergeState.id)
        ).scalars().all()
        return [_incremental_child_merge_state_snapshot(row) for row in rows]


def get_parent_incremental_merge_lane(
    session_factory: sessionmaker[Session],
    *,
    parent_node_version_id: UUID,
) -> ParentIncrementalMergeLaneSnapshot | None:
    with query_session_scope(session_factory) as session:
        row = session.get(ParentIncrementalMergeLane, parent_node_version_id)
        if row is None:
            return None
        return _parent_incremental_merge_lane_snapshot(row)


def process_pending_incremental_parent_merges(
    session_factory: sessionmaker[Session],
) -> list[IncrementalParentMergeExecutionSnapshot]:
    with query_session_scope(session_factory) as session:
        parent_node_version_ids = [
            row.parent_node_version_id
            for row in session.execute(
                select(ParentIncrementalMergeLane)
                .where(ParentIncrementalMergeLane.status.in_(("pending", "running")))
                .order_by(ParentIncrementalMergeLane.updated_at, ParentIncrementalMergeLane.created_at)
            ).scalars()
        ]

    snapshots: list[IncrementalParentMergeExecutionSnapshot] = []
    for parent_node_version_id in parent_node_version_ids:
        result = process_next_incremental_child_merge(
            session_factory,
            parent_node_version_id=parent_node_version_id,
        )
        if result is not None:
            snapshots.append(result)
    return snapshots


def process_next_incremental_child_merge(
    session_factory: sessionmaker[Session],
    *,
    parent_node_version_id: UUID,
) -> IncrementalParentMergeExecutionSnapshot | None:
    with session_scope(session_factory) as session:
        parent_version = session.get(NodeVersion, parent_node_version_id)
        if parent_version is None:
            return None
        _lock_parent_lane(session, logical_node_id=parent_version.logical_node_id)
        lane = session.get(ParentIncrementalMergeLane, parent_node_version_id)
        if lane is None:
            return None

        parent_selector = session.get(LogicalNodeCurrentVersion, parent_version.logical_node_id)
        if parent_selector is None or parent_selector.authoritative_node_version_id != parent_node_version_id:
            lane.status = "superseded"
            lane.blocked_reason = "parent_superseded"
            session.flush()
            return None

        if has_unresolved_merge_conflicts(session, node_version_id=parent_node_version_id):
            lane.status = "blocked"
            lane.blocked_reason = "unresolved_merge_conflict"
            session.flush()
            return None

        row = _load_next_completed_unmerged_child(session, parent_node_version_id=parent_node_version_id)
        while row is not None and not _is_mergeable_child_for_parent(session, row=row, parent_node_version_id=parent_node_version_id):
            row.status = "superseded"
            session.flush()
            row = _load_next_completed_unmerged_child(session, parent_node_version_id=parent_node_version_id)

        if row is None:
            lane.status = "idle"
            lane.blocked_reason = None
            session.flush()
            return None

        parent_repo_path = _repo_path(parent_node_version_id)
        child_repo_path = _repo_path(row.child_node_version_id)
        if not parent_repo_path.exists():
            raise DaemonConflictError("parent live git repo has not been bootstrapped")
        if not child_repo_path.exists():
            raise DaemonConflictError("child live git repo has not been bootstrapped")

        parent_branch = _require_branch_name(parent_version)
        parent_commit_before = lane.current_parent_head_commit_sha or parent_version.final_commit_sha or parent_version.seed_commit_sha
        if parent_commit_before is None:
            raise DaemonConflictError("incremental parent merge requires a recorded parent head commit")

        lane.status = "running"
        lane.blocked_reason = None
        _git(parent_repo_path, "checkout", parent_branch)
        current_head = _git_output(parent_repo_path, "rev-parse", "HEAD")
        if current_head != parent_commit_before:
            _git(parent_repo_path, "reset", "--hard", parent_commit_before)

        merge_order = _next_applied_merge_order(session, parent_node_version_id=parent_node_version_id)
        fetch_result = _git_try(parent_repo_path, "fetch", str(child_repo_path), row.child_final_commit_sha)
        if not fetch_result.ok:
            raise DaemonConflictError(fetch_result.message)
        merge_result = _git_try(parent_repo_path, "merge", "--no-ff", "--no-edit", "FETCH_HEAD")
        if not merge_result.ok:
            conflicted_files = _git_output(parent_repo_path, "diff", "--name-only", "--diff-filter=U").splitlines()
            conflict = record_merge_conflict_in_session(
                session,
                parent_node_version_id=parent_node_version_id,
                child_node_version_id=row.child_node_version_id,
                child_final_commit_sha=row.child_final_commit_sha,
                parent_commit_before=parent_commit_before,
                parent_commit_after=parent_commit_before,
                merge_order=merge_order,
                files_json=conflicted_files or ["unknown_conflict"],
            )
            row.status = "conflicted"
            row.parent_commit_before = parent_commit_before
            row.parent_commit_after = parent_commit_before
            row.conflict_id = conflict.id
            lane.status = "blocked"
            lane.blocked_reason = "merge_conflict"
            _set_working_tree_state_in_session(session, logical_node_id=parent_version.logical_node_id, state="merge_conflict")
            _persist_incremental_merge_conflict_context_in_session(
                session,
                parent_version=parent_version,
                row=row,
                conflict=conflict,
                merge_order=merge_order,
                lane=lane,
            )
            session.flush()
            return IncrementalParentMergeExecutionSnapshot(
                parent_node_version_id=parent_node_version_id,
                child_node_version_id=row.child_node_version_id,
                status="conflicted",
                applied_merge_order=None,
                parent_commit_before=parent_commit_before,
                parent_commit_after=parent_commit_before,
                conflict_id=conflict.id,
                lane_status=lane.status,
            )

        parent_commit_after = _git_output(parent_repo_path, "rev-parse", "HEAD")
        record_merge_event_in_session(
            session,
            parent_node_version_id=parent_node_version_id,
            child_node_version_id=row.child_node_version_id,
            child_final_commit_sha=row.child_final_commit_sha,
            parent_commit_before=parent_commit_before,
            parent_commit_after=parent_commit_after,
            merge_order=merge_order,
            had_conflict=False,
        )
        row.status = "merged"
        row.applied_merge_order = merge_order
        row.parent_commit_before = parent_commit_before
        row.parent_commit_after = parent_commit_after
        row.conflict_id = None
        lane.current_parent_head_commit_sha = parent_commit_after
        lane.last_successful_merge_at = datetime.now(timezone.utc)
        lane.blocked_reason = None
        session.flush()
        lane.status = "pending" if _has_remaining_completed_unmerged(session, parent_node_version_id=parent_node_version_id) else "idle"
        _set_working_tree_state_in_session(session, logical_node_id=parent_version.logical_node_id, state="merged_children")
        session.flush()
        return IncrementalParentMergeExecutionSnapshot(
            parent_node_version_id=parent_node_version_id,
            child_node_version_id=row.child_node_version_id,
            status="merged",
            applied_merge_order=merge_order,
            parent_commit_before=parent_commit_before,
            parent_commit_after=parent_commit_after,
            conflict_id=None,
            lane_status=lane.status,
        )


def _incremental_child_merge_state_snapshot(row: IncrementalChildMergeState) -> IncrementalChildMergeStateSnapshot:
    return IncrementalChildMergeStateSnapshot(
        id=row.id,
        parent_node_version_id=row.parent_node_version_id,
        child_node_version_id=row.child_node_version_id,
        child_final_commit_sha=row.child_final_commit_sha,
        status=row.status,
        applied_merge_order=row.applied_merge_order,
        parent_commit_before=row.parent_commit_before,
        parent_commit_after=row.parent_commit_after,
        conflict_id=row.conflict_id,
    )


def _parent_incremental_merge_lane_snapshot(row: ParentIncrementalMergeLane) -> ParentIncrementalMergeLaneSnapshot:
    return ParentIncrementalMergeLaneSnapshot(
        parent_node_version_id=row.parent_node_version_id,
        status=row.status,
        current_parent_head_commit_sha=row.current_parent_head_commit_sha,
        last_successful_merge_at=None if row.last_successful_merge_at is None else row.last_successful_merge_at.isoformat(),
        blocked_reason=row.blocked_reason,
    )


def _lock_parent_lane(session: Session, *, logical_node_id: UUID) -> None:
    session.execute(text("select pg_advisory_xact_lock(hashtext(:node_id))"), {"node_id": str(logical_node_id)})


def _load_next_completed_unmerged_child(session: Session, *, parent_node_version_id: UUID) -> IncrementalChildMergeState | None:
    return session.execute(
        select(IncrementalChildMergeState)
        .where(
            IncrementalChildMergeState.parent_node_version_id == parent_node_version_id,
            IncrementalChildMergeState.status == "completed_unmerged",
        )
        .order_by(IncrementalChildMergeState.created_at, IncrementalChildMergeState.id)
    ).scalars().first()


def _is_mergeable_child_for_parent(session: Session, *, row: IncrementalChildMergeState, parent_node_version_id: UUID) -> bool:
    child_version = session.get(NodeVersion, row.child_node_version_id)
    if child_version is None or child_version.parent_node_version_id != parent_node_version_id:
        return False
    if child_version.final_commit_sha != row.child_final_commit_sha:
        return False
    selector = session.get(LogicalNodeCurrentVersion, child_version.logical_node_id)
    return selector is not None and selector.authoritative_node_version_id == child_version.id


def _next_applied_merge_order(session: Session, *, parent_node_version_id: UUID) -> int:
    current = session.execute(
        select(func.max(IncrementalChildMergeState.applied_merge_order)).where(
            IncrementalChildMergeState.parent_node_version_id == parent_node_version_id
        )
    ).scalar_one()
    return int(current or 0) + 1


def _has_remaining_completed_unmerged(session: Session, *, parent_node_version_id: UUID) -> bool:
    return (
        session.execute(
            select(IncrementalChildMergeState.id).where(
                IncrementalChildMergeState.parent_node_version_id == parent_node_version_id,
                IncrementalChildMergeState.status == "completed_unmerged",
            )
        ).first()
        is not None
    )


def _set_working_tree_state_in_session(session: Session, *, logical_node_id: UUID, state: str) -> None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None:
        lifecycle = NodeLifecycleState(node_id=str(logical_node_id), lifecycle_state="DRAFT", working_tree_state=state)
        session.add(lifecycle)
    else:
        lifecycle.working_tree_state = state


def _persist_incremental_merge_conflict_context_in_session(
    session: Session,
    *,
    parent_version: NodeVersion,
    row: IncrementalChildMergeState,
    conflict,
    merge_order: int,
    lane: ParentIncrementalMergeLane,
) -> None:
    context_json = {
        "context_kind": "incremental_merge_conflict",
        "status": "blocked_on_incremental_merge_conflict",
        "blocking_reasons": ["parent incremental merge lane is blocked on an unresolved merge conflict"],
        "reconcile_prompt_relative_path": RECONCILE_PROMPT_PATH,
        "incremental_merge_conflict": {
            "conflict_id": str(conflict.id),
            "parent_node_id": str(parent_version.logical_node_id),
            "parent_node_version_id": str(parent_version.id),
            "child_node_version_id": str(row.child_node_version_id),
            "child_final_commit_sha": row.child_final_commit_sha,
            "parent_commit_before": row.parent_commit_before,
            "parent_commit_after": row.parent_commit_after,
            "merge_order": merge_order,
            "files_json": list(conflict.files_json),
            "resolution_status": conflict.resolution_status,
            "resolution_summary": conflict.resolution_summary,
            "lane_status": lane.status,
            "lane_blocked_reason": lane.blocked_reason,
        },
    }
    _persist_parent_reconcile_context_in_session(
        session,
        logical_node_id=parent_version.logical_node_id,
        parent_version_id=parent_version.id,
        context_json=context_json,
    )


def _persist_parent_reconcile_context_in_session(
    session: Session,
    *,
    logical_node_id: UUID,
    parent_version_id: UUID,
    context_json: dict[str, object],
) -> None:
    active_run = session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == parent_version_id, NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")))
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if active_run is None:
        return
    state = session.get(NodeRunState, active_run.id)
    if state is None:
        return
    cursor = dict(state.execution_cursor_json or {})
    cursor["parent_reconcile_context"] = context_json
    state.execution_cursor_json = cursor
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is not None:
        lifecycle.execution_cursor_json = dict(cursor)
