from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import LogicalNodeCurrentVersion, NodeVersion
from aicoding.db.session import query_session_scope, session_scope

COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{7,64}$")
MUTABLE_BRANCH_STATUSES = {"authoritative", "candidate"}


@dataclass(frozen=True, slots=True)
class BranchMetadataSnapshot:
    node_version_id: UUID
    logical_node_id: UUID
    version_number: int
    title: str
    tier: str
    node_kind: str
    node_status: str
    active_branch_name: str | None
    expected_branch_name: str
    branch_generation_number: int | None
    expected_branch_generation_number: int
    seed_commit_sha: str | None
    final_commit_sha: str | None
    branch_status: str
    violations: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "version_number": self.version_number,
            "title": self.title,
            "tier": self.tier,
            "node_kind": self.node_kind,
            "node_status": self.node_status,
            "active_branch_name": self.active_branch_name,
            "expected_branch_name": self.expected_branch_name,
            "branch_generation_number": self.branch_generation_number,
            "expected_branch_generation_number": self.expected_branch_generation_number,
            "seed_commit_sha": self.seed_commit_sha,
            "final_commit_sha": self.final_commit_sha,
            "branch_status": self.branch_status,
            "violations": self.violations,
        }


def build_canonical_branch_name(*, tier: str, kind: str, title: str, logical_node_id: UUID, version_number: int) -> str:
    return (
        f"tier/{_sanitize_component(tier)}/{_sanitize_component(kind)}/"
        f"{_slugify_title(title)}__{logical_node_id.hex}/v{version_number}"
    )


def inherited_seed_commit(previous: NodeVersion) -> str | None:
    return previous.final_commit_sha or previous.seed_commit_sha


def load_node_branch_metadata(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> BranchMetadataSnapshot:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        return _snapshot(session.get(NodeVersion, selector.authoritative_node_version_id))


def load_node_version_branch_metadata(session_factory: sessionmaker[Session], *, version_id: UUID) -> BranchMetadataSnapshot:
    with query_session_scope(session_factory) as session:
        return _snapshot(session.get(NodeVersion, version_id))


def record_seed_commit(session_factory: sessionmaker[Session], *, version_id: UUID, commit_sha: str) -> BranchMetadataSnapshot:
    normalized = _normalize_commit_sha(commit_sha)
    with session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        _ensure_mutable_branch_status(version)
        if version.seed_commit_sha is not None and version.seed_commit_sha != normalized:
            raise DaemonConflictError("seed commit is immutable once recorded")
        version.seed_commit_sha = normalized
        session.flush()
        return _snapshot(version)


def record_final_commit(session_factory: sessionmaker[Session], *, version_id: UUID, commit_sha: str) -> BranchMetadataSnapshot:
    normalized = _normalize_commit_sha(commit_sha)
    with session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        _ensure_mutable_branch_status(version)
        if version.seed_commit_sha is None:
            raise DaemonConflictError("final commit requires a recorded seed commit")
        if version.final_commit_sha is not None and version.final_commit_sha != normalized:
            raise DaemonConflictError("final commit is immutable once recorded")
        version.final_commit_sha = normalized
        session.flush()
        return _snapshot(version)


def _snapshot(version: NodeVersion | None) -> BranchMetadataSnapshot:
    if version is None:
        raise DaemonNotFoundError("node version not found")
    expected_branch_name = build_canonical_branch_name(
        tier=version.tier,
        kind=version.node_kind,
        title=version.title,
        logical_node_id=version.logical_node_id,
        version_number=version.version_number,
    )
    expected_generation = version.version_number
    violations: list[str] = []
    if version.active_branch_name != expected_branch_name:
        violations.append("branch_name_mismatch")
    if version.branch_generation_number != expected_generation:
        violations.append("branch_generation_mismatch")
    return BranchMetadataSnapshot(
        node_version_id=version.id,
        logical_node_id=version.logical_node_id,
        version_number=version.version_number,
        title=version.title,
        tier=version.tier,
        node_kind=version.node_kind,
        node_status=version.status,
        active_branch_name=version.active_branch_name,
        expected_branch_name=expected_branch_name,
        branch_generation_number=version.branch_generation_number,
        expected_branch_generation_number=expected_generation,
        seed_commit_sha=version.seed_commit_sha,
        final_commit_sha=version.final_commit_sha,
        branch_status="valid" if not violations else "stale",
        violations=violations,
    )


def _require_version(session: Session, version_id: UUID) -> NodeVersion:
    version = session.get(NodeVersion, version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _ensure_mutable_branch_status(version: NodeVersion) -> None:
    if version.status not in MUTABLE_BRANCH_STATUSES:
        raise DaemonConflictError(f"branch metadata may not be updated for status '{version.status}'")


def _normalize_commit_sha(commit_sha: str) -> str:
    normalized = commit_sha.strip().lower()
    if not COMMIT_SHA_PATTERN.match(normalized):
        raise DaemonConflictError("commit sha must be 7 to 64 lowercase hex characters")
    return normalized


def _slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "node"


def _sanitize_component(value: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return sanitized or "unknown"
