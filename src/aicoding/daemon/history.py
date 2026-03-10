from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.db.models import CompiledSubtask, LogicalNodeCurrentVersion, NodeVersion, PromptRecord, SummaryRecord
from aicoding.db.session import query_session_scope

PROMPT_ROLE_BY_SUBTASK_TYPE = {
    "review": "review_prompt",
    "run_tests": "testing_prompt",
    "build_docs": "docs_prompt",
}


@dataclass(frozen=True, slots=True)
class PromptRecordSnapshot:
    id: UUID
    node_version_id: UUID
    node_run_id: UUID
    compiled_subtask_id: UUID | None
    prompt_role: str
    source_subtask_key: str | None
    template_path: str | None
    template_hash: str | None
    content: str
    content_hash: str
    payload_json: dict[str, object]
    delivered_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "prompt_role": self.prompt_role,
            "source_subtask_key": self.source_subtask_key,
            "template_path": self.template_path,
            "template_hash": self.template_hash,
            "content": self.content,
            "content_hash": self.content_hash,
            "payload_json": self.payload_json,
            "delivered_at": self.delivered_at,
        }


@dataclass(frozen=True, slots=True)
class PromptHistoryCatalogSnapshot:
    node_id: UUID
    prompts: list[PromptRecordSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"node_id": str(self.node_id), "prompts": [item.to_payload() for item in self.prompts]}


@dataclass(frozen=True, slots=True)
class SummaryRecordSnapshot:
    id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    attempt_number: int | None
    summary_type: str
    summary_scope: str
    summary_path: str | None
    content: str
    content_hash: str
    metadata_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "attempt_number": self.attempt_number,
            "summary_type": self.summary_type,
            "summary_scope": self.summary_scope,
            "summary_path": self.summary_path,
            "content": self.content,
            "content_hash": self.content_hash,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class SummaryHistoryCatalogSnapshot:
    node_id: UUID
    summaries: list[SummaryRecordSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"node_id": str(self.node_id), "summaries": [item.to_payload() for item in self.summaries]}


def record_prompt_delivery(
    session: Session,
    *,
    node_version_id: UUID,
    node_run_id: UUID,
    compiled_subtask: CompiledSubtask | None,
    content: str,
    payload_json: dict[str, object],
) -> PromptRecordSnapshot:
    prompt_role = "subtask_prompt"
    if compiled_subtask is not None:
        prompt_role = PROMPT_ROLE_BY_SUBTASK_TYPE.get(compiled_subtask.subtask_type, "subtask_prompt")
    row = PromptRecord(
        id=uuid4(),
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        compiled_subtask_id=None if compiled_subtask is None else compiled_subtask.id,
        prompt_role=prompt_role,
        source_subtask_key=None if compiled_subtask is None else compiled_subtask.source_subtask_key,
        template_path=None if compiled_subtask is None else compiled_subtask.source_file_path,
        template_hash=None if compiled_subtask is None else compiled_subtask.source_hash,
        content=content,
        content_hash=sha256(content.encode("utf-8")).hexdigest(),
        payload_json=dict(payload_json),
    )
    session.add(row)
    session.flush()
    return _prompt_snapshot(row)


def record_summary_history(
    session: Session,
    *,
    node_version_id: UUID,
    node_run_id: UUID | None,
    compiled_subtask_id: UUID | None,
    attempt_number: int | None,
    summary_type: str,
    summary_scope: str,
    summary_path: str | None,
    content: str,
    metadata_json: dict[str, object] | None = None,
) -> SummaryRecordSnapshot:
    row = SummaryRecord(
        id=uuid4(),
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        compiled_subtask_id=compiled_subtask_id,
        attempt_number=attempt_number,
        summary_type=summary_type,
        summary_scope=summary_scope,
        summary_path=summary_path,
        content=content,
        content_hash=sha256(content.encode("utf-8")).hexdigest(),
        metadata_json={} if metadata_json is None else dict(metadata_json),
    )
    session.add(row)
    session.flush()
    return _summary_snapshot(row)


def list_prompt_history(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> PromptHistoryCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        version_ids = _node_version_ids(session, logical_node_id)
        rows = session.execute(
            select(PromptRecord)
            .where(PromptRecord.node_version_id.in_(version_ids))
            .order_by(PromptRecord.delivered_at, PromptRecord.id)
        ).scalars().all()
        return PromptHistoryCatalogSnapshot(node_id=logical_node_id, prompts=[_prompt_snapshot(row) for row in rows])


def get_prompt_record(session_factory: sessionmaker[Session], *, prompt_id: UUID) -> PromptRecordSnapshot:
    with query_session_scope(session_factory) as session:
        row = session.get(PromptRecord, prompt_id)
        if row is None:
            raise DaemonNotFoundError("prompt history record not found")
        return _prompt_snapshot(row)


def list_summary_history(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> SummaryHistoryCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        version_ids = _node_version_ids(session, logical_node_id)
        rows = session.execute(
            select(SummaryRecord)
            .where(SummaryRecord.node_version_id.in_(version_ids))
            .order_by(SummaryRecord.created_at, SummaryRecord.id)
        ).scalars().all()
        return SummaryHistoryCatalogSnapshot(node_id=logical_node_id, summaries=[_summary_snapshot(row) for row in rows])


def get_summary_record(session_factory: sessionmaker[Session], *, summary_id: UUID) -> SummaryRecordSnapshot:
    with query_session_scope(session_factory) as session:
        row = session.get(SummaryRecord, summary_id)
        if row is None:
            raise DaemonNotFoundError("summary history record not found")
        return _summary_snapshot(row)


def has_registered_summary(
    session: Session,
    *,
    node_run_id: UUID,
    compiled_subtask_id: UUID | None,
    summary_path: str,
) -> bool:
    row = session.execute(
        select(SummaryRecord.id).where(
            SummaryRecord.node_run_id == node_run_id,
            SummaryRecord.summary_path == summary_path,
            SummaryRecord.compiled_subtask_id == compiled_subtask_id,
        )
    ).first()
    return row is not None


def _node_version_ids(session: Session, logical_node_id: UUID) -> list[UUID]:
    current = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if current is None:
        raise DaemonNotFoundError("logical node version selector not found")
    rows = session.execute(select(NodeVersion.id).where(NodeVersion.logical_node_id == logical_node_id)).all()
    return [row[0] for row in rows] or [current.authoritative_node_version_id]


def _prompt_snapshot(row: PromptRecord) -> PromptRecordSnapshot:
    return PromptRecordSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        prompt_role=row.prompt_role,
        source_subtask_key=row.source_subtask_key,
        template_path=row.template_path,
        template_hash=row.template_hash,
        content=row.content,
        content_hash=row.content_hash,
        payload_json=dict(row.payload_json or {}),
        delivered_at=row.delivered_at.astimezone(timezone.utc).isoformat(),
    )


def _summary_snapshot(row: SummaryRecord) -> SummaryRecordSnapshot:
    return SummaryRecordSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        attempt_number=row.attempt_number,
        summary_type=row.summary_type,
        summary_scope=row.summary_scope,
        summary_path=row.summary_path,
        content=row.content,
        content_hash=row.content_hash,
        metadata_json=dict(row.metadata_json or {}),
        created_at=row.created_at.astimezone(timezone.utc).isoformat(),
    )
