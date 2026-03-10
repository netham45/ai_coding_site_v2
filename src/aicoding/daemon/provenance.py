from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass
from datetime import timezone
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, aliased, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.config import get_settings
from aicoding.daemon.history import record_summary_history
from aicoding.db.models import (
    CodeEntity,
    CodeRelation,
    LogicalNodeCurrentVersion,
    NodeEntityChange,
    NodeVersion,
    PromptRecord,
    SummaryRecord,
)
from aicoding.db.session import query_session_scope, session_scope

IGNORED_DIR_NAMES = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".runtime"}
SUPPORTED_ENTITY_TYPES = {"module", "class", "function", "method"}
CHANGED_ENTITY_TYPES = {"added", "modified", "renamed_or_moved"}
SUPPORTED_SCRIPT_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx"}
JS_KEYWORD_CALL_NAMES = {"if", "for", "while", "switch", "catch", "return", "typeof", "new", "function", "class"}


@dataclass(frozen=True, slots=True)
class ObservedRelation:
    from_canonical_name: str
    to_canonical_name: str
    relation_type: str
    source: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ObservedEntity:
    language: str
    entity_type: str
    canonical_name: str
    file_path: str
    signature: str | None
    start_line: int | None
    end_line: int | None
    stable_hash: str


@dataclass(frozen=True, slots=True)
class EntitySnapshot:
    id: UUID
    entity_type: str
    canonical_name: str
    file_path: str | None
    signature: str | None
    start_line: int | None
    end_line: int | None
    stable_hash: str | None
    created_at: str
    updated_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "entity_type": self.entity_type,
            "canonical_name": self.canonical_name,
            "file_path": self.file_path,
            "signature": self.signature,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "stable_hash": self.stable_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True, slots=True)
class EntityHistoryEntrySnapshot:
    id: UUID
    node_version_id: UUID
    logical_node_id: UUID
    entity_id: UUID
    prompt_record_id: UUID | None
    summary_record_id: UUID | None
    change_type: str
    match_confidence: str
    match_reason: str
    rationale_summary: str | None
    observed_canonical_name: str
    observed_file_path: str | None
    observed_signature: str | None
    observed_stable_hash: str | None
    metadata_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "entity_id": str(self.entity_id),
            "prompt_record_id": None if self.prompt_record_id is None else str(self.prompt_record_id),
            "summary_record_id": None if self.summary_record_id is None else str(self.summary_record_id),
            "change_type": self.change_type,
            "match_confidence": self.match_confidence,
            "match_reason": self.match_reason,
            "rationale_summary": self.rationale_summary,
            "observed_canonical_name": self.observed_canonical_name,
            "observed_file_path": self.observed_file_path,
            "observed_signature": self.observed_signature,
            "observed_stable_hash": self.observed_stable_hash,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class EntityRelationSnapshot:
    id: UUID
    node_version_id: UUID
    from_entity_id: UUID
    from_canonical_name: str
    to_entity_id: UUID
    to_canonical_name: str
    relation_type: str
    source: str
    confidence: float | None
    rationale_summary: str | None
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "from_entity_id": str(self.from_entity_id),
            "from_canonical_name": self.from_canonical_name,
            "to_entity_id": str(self.to_entity_id),
            "to_canonical_name": self.to_canonical_name,
            "relation_type": self.relation_type,
            "source": self.source,
            "confidence": self.confidence,
            "rationale_summary": self.rationale_summary,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class EntityCatalogSnapshot:
    canonical_name: str
    entities: list[EntitySnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"canonical_name": self.canonical_name, "entities": [item.to_payload() for item in self.entities]}


@dataclass(frozen=True, slots=True)
class EntityHistoryCatalogSnapshot:
    canonical_name: str
    history: list[EntityHistoryEntrySnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"canonical_name": self.canonical_name, "history": [item.to_payload() for item in self.history]}


@dataclass(frozen=True, slots=True)
class EntityRelationCatalogSnapshot:
    canonical_name: str
    relations: list[EntityRelationSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"canonical_name": self.canonical_name, "relations": [item.to_payload() for item in self.relations]}


@dataclass(frozen=True, slots=True)
class RationaleSnapshot:
    node_id: UUID
    node_version_id: UUID
    prompt_record_id: UUID | None
    summary_record_id: UUID | None
    rationale_summary: str
    change_counts: dict[str, int]
    entity_history: list[EntityHistoryEntrySnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "prompt_record_id": None if self.prompt_record_id is None else str(self.prompt_record_id),
            "summary_record_id": None if self.summary_record_id is None else str(self.summary_record_id),
            "rationale_summary": self.rationale_summary,
            "change_counts": self.change_counts,
            "entity_history": [item.to_payload() for item in self.entity_history],
        }


@dataclass(frozen=True, slots=True)
class ProvenanceRefreshSnapshot:
    node_id: UUID
    node_version_id: UUID
    prompt_record_id: UUID | None
    summary_record_id: UUID | None
    provenance_summary_id: UUID
    rationale_summary: str
    entity_count: int
    relation_count: int
    change_counts: dict[str, int]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "prompt_record_id": None if self.prompt_record_id is None else str(self.prompt_record_id),
            "summary_record_id": None if self.summary_record_id is None else str(self.summary_record_id),
            "provenance_summary_id": str(self.provenance_summary_id),
            "rationale_summary": self.rationale_summary,
            "entity_count": self.entity_count,
            "relation_count": self.relation_count,
            "change_counts": self.change_counts,
        }


def refresh_node_provenance(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    workspace_root: Path | None = None,
) -> ProvenanceRefreshSnapshot:
    settings_workspace_root = get_settings().workspace_root
    workspace_root = workspace_root or settings_workspace_root or Path.cwd()
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        prompt_row = _latest_prompt_row(session, version.id)
        summary_row = _latest_summary_row(session, version.id)
        rationale_summary = _build_rationale_summary(version, prompt_row, summary_row)
        observed_entities, observed_relations = _extract_workspace_entities(workspace_root)
        _replace_node_provenance(
            session,
            version=version,
            observed_entities=observed_entities,
            observed_relations=observed_relations,
            prompt_row=prompt_row,
            summary_row=summary_row,
            rationale_summary=rationale_summary,
        )
        changes = _history_rows_for_version(session, version.id)
        relation_count = session.execute(
            select(CodeRelation).where(CodeRelation.node_version_id == version.id)
        ).scalars().all()
        provenance_summary = record_summary_history(
            session,
            node_version_id=version.id,
            node_run_id=None,
            compiled_subtask_id=None,
            attempt_number=None,
            summary_type="provenance",
            summary_scope="node_version",
            summary_path=f"provenance://{version.id}",
            content=rationale_summary,
            metadata_json={
                "entity_count": len(observed_entities),
                "relation_count": len(relation_count),
                "change_counts": _count_change_types(changes),
            },
        )
        return ProvenanceRefreshSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            prompt_record_id=None if prompt_row is None else prompt_row.id,
            summary_record_id=None if summary_row is None else summary_row.id,
            provenance_summary_id=provenance_summary.id,
            rationale_summary=rationale_summary,
            entity_count=len(observed_entities),
            relation_count=len(relation_count),
            change_counts=_count_change_types(changes),
        )


def show_node_rationale(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> RationaleSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        prompt_row = _latest_prompt_row(session, version.id)
        summary_row = _latest_summary_row(session, version.id, include_provenance=True)
        changes = _history_rows_for_version(session, version.id)
        if not changes:
            raise DaemonNotFoundError("node rationale not found")
        return RationaleSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            prompt_record_id=None if prompt_row is None else prompt_row.id,
            summary_record_id=None if summary_row is None else summary_row.id,
            rationale_summary=_build_rationale_summary(version, prompt_row, summary_row),
            change_counts=_count_change_types(changes),
            entity_history=[_history_snapshot(session, row) for row in changes],
        )


def show_entity_by_name(session_factory: sessionmaker[Session], *, canonical_name: str) -> EntityCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(CodeEntity).where(CodeEntity.canonical_name == canonical_name).order_by(CodeEntity.entity_type, CodeEntity.file_path)
        ).scalars().all()
        if not rows:
            raise DaemonNotFoundError("entity not found")
        return EntityCatalogSnapshot(canonical_name=canonical_name, entities=[_entity_snapshot(row) for row in rows])


def show_entity_history(session_factory: sessionmaker[Session], *, canonical_name: str, changed_only: bool = False) -> EntityHistoryCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        rows = _entity_history_query(session, canonical_name=canonical_name, changed_only=changed_only)
        if not rows:
            raise DaemonNotFoundError("entity history not found")
        return EntityHistoryCatalogSnapshot(canonical_name=canonical_name, history=[_history_snapshot(session, row) for row in rows])


def show_entity_relations(session_factory: sessionmaker[Session], *, canonical_name: str) -> EntityRelationCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        from_entity = aliased(CodeEntity)
        to_entity = aliased(CodeEntity)
        rows = session.execute(
            select(CodeRelation, from_entity.canonical_name, to_entity.canonical_name)
            .join(from_entity, from_entity.id == CodeRelation.from_entity_id)
            .join(to_entity, to_entity.id == CodeRelation.to_entity_id)
            .where(or_(from_entity.canonical_name == canonical_name, to_entity.canonical_name == canonical_name))
            .order_by(CodeRelation.created_at, CodeRelation.id)
        ).all()
        if not rows:
            raise DaemonNotFoundError("entity relations not found")
        return EntityRelationCatalogSnapshot(
            canonical_name=canonical_name,
            relations=[_relation_snapshot(relation, from_name, to_name) for relation, from_name, to_name in rows],
        )


def _replace_node_provenance(
    session: Session,
    *,
    version: NodeVersion,
    observed_entities: list[ObservedEntity],
    observed_relations: list[ObservedRelation],
    prompt_row: PromptRecord | None,
    summary_row: SummaryRecord | None,
    rationale_summary: str,
) -> None:
    session.execute(delete(NodeEntityChange).where(NodeEntityChange.node_version_id == version.id))
    session.execute(delete(CodeRelation).where(CodeRelation.node_version_id == version.id))
    existing_entities = session.execute(select(CodeEntity).where(CodeEntity.entity_type.in_(SUPPORTED_ENTITY_TYPES))).scalars().all()
    previous_entity_ids = _previous_version_entity_ids(session, version)
    current_entity_ids: set[UUID] = set()
    observed_lookup: dict[str, CodeEntity] = {}
    for observed in observed_entities:
        matched_entity, change_type, match_confidence, match_reason = _match_or_create_entity(session, existing_entities, observed)
        current_entity_ids.add(matched_entity.id)
        observed_lookup[observed.canonical_name] = matched_entity
        session.add(
            NodeEntityChange(
                id=uuid4(),
                node_version_id=version.id,
                entity_id=matched_entity.id,
                prompt_record_id=None if prompt_row is None else prompt_row.id,
                summary_record_id=None if summary_row is None else summary_row.id,
                change_type=change_type,
                match_confidence=match_confidence,
                match_reason=match_reason,
                rationale_summary=rationale_summary,
                observed_canonical_name=observed.canonical_name,
                observed_file_path=observed.file_path,
                observed_signature=observed.signature,
                observed_stable_hash=observed.stable_hash,
                metadata_json={"entity_type": observed.entity_type, "language": observed.language},
            )
        )
    removed_ids = previous_entity_ids - current_entity_ids
    for entity_id in sorted(removed_ids):
        entity = session.get(CodeEntity, entity_id)
        if entity is None:
            continue
        session.add(
            NodeEntityChange(
                id=uuid4(),
                node_version_id=version.id,
                entity_id=entity.id,
                prompt_record_id=None if prompt_row is None else prompt_row.id,
                summary_record_id=None if summary_row is None else summary_row.id,
                change_type="removed",
                match_confidence="high",
                match_reason="removed_from_snapshot",
                rationale_summary=rationale_summary,
                observed_canonical_name=entity.canonical_name,
                observed_file_path=entity.file_path,
                observed_signature=entity.signature,
                observed_stable_hash=entity.stable_hash,
                metadata_json={"entity_type": entity.entity_type, "language": _language_for_path(entity.file_path)},
            )
        )
    session.flush()
    for relation in observed_relations:
        from_entity = observed_lookup.get(relation.from_canonical_name)
        to_entity = observed_lookup.get(relation.to_canonical_name)
        if from_entity is None or to_entity is None or from_entity.id == to_entity.id:
            continue
        session.add(
            CodeRelation(
                id=uuid4(),
                node_version_id=version.id,
                from_entity_id=from_entity.id,
                to_entity_id=to_entity.id,
                relation_type=relation.relation_type,
                source=relation.source,
                confidence=relation.confidence,
                rationale_summary=rationale_summary,
            )
        )
    session.flush()


def _match_or_create_entity(
    session: Session,
    existing_entities: list[CodeEntity],
    observed: ObservedEntity,
) -> tuple[CodeEntity, str, str, str]:
    exact_matches = [
        entity
        for entity in existing_entities
        if entity.entity_type == observed.entity_type
        and entity.canonical_name == observed.canonical_name
        and entity.file_path == observed.file_path
        and entity.signature == observed.signature
    ]
    if len(exact_matches) == 1:
        entity = exact_matches[0]
        change_type = "unchanged" if entity.stable_hash == observed.stable_hash else "modified"
        _update_entity_anchor(entity, observed)
        session.flush()
        return entity, change_type, "high", "exact_match"
    heuristic_matches = [
        entity
        for entity in existing_entities
        if entity.entity_type == observed.entity_type
        and entity.signature == observed.signature
        and entity.stable_hash == observed.stable_hash
        and (entity.canonical_name != observed.canonical_name or entity.file_path != observed.file_path)
    ]
    if len(heuristic_matches) == 1:
        entity = heuristic_matches[0]
        _update_entity_anchor(entity, observed)
        session.flush()
        return entity, "renamed_or_moved", "medium", "heuristic_match"
    entity = CodeEntity(
        id=uuid4(),
        entity_type=observed.entity_type,
        canonical_name=observed.canonical_name,
        file_path=observed.file_path,
        signature=observed.signature,
        start_line=observed.start_line,
        end_line=observed.end_line,
        stable_hash=observed.stable_hash,
    )
    session.add(entity)
    existing_entities.append(entity)
    session.flush()
    return entity, "added", "high", "new_entity"


def _update_entity_anchor(entity: CodeEntity, observed: ObservedEntity) -> None:
    entity.canonical_name = observed.canonical_name
    entity.file_path = observed.file_path
    entity.signature = observed.signature
    entity.start_line = observed.start_line
    entity.end_line = observed.end_line
    entity.stable_hash = observed.stable_hash


def _previous_version_entity_ids(session: Session, version: NodeVersion) -> set[UUID]:
    previous_version_id = version.supersedes_node_version_id
    if previous_version_id is None:
        return set()
    rows = session.execute(
        select(NodeEntityChange.entity_id, NodeEntityChange.change_type)
        .where(NodeEntityChange.node_version_id == previous_version_id)
    ).all()
    return {entity_id for entity_id, change_type in rows if change_type != "removed"}


def _extract_workspace_entities(workspace_root: Path) -> tuple[list[ObservedEntity], list[ObservedRelation]]:
    if not workspace_root.exists():
        raise DaemonConflictError("workspace root does not exist for provenance extraction")
    entities: list[ObservedEntity] = []
    relations: list[ObservedRelation] = []
    for path in sorted(_iter_source_files(workspace_root)):
        parser = _PythonEntityExtractor(workspace_root, path) if path.suffix == ".py" else _ScriptEntityExtractor(workspace_root, path)
        parser.extract()
        entities.extend(parser.entities)
        relations.extend(parser.relations)
    if not entities:
        raise DaemonConflictError("no supported source entities found in workspace")
    return entities, relations


def _iter_source_files(workspace_root: Path) -> list[Path]:
    files: list[Path] = []
    scan_root = workspace_root / "src" if (workspace_root / "src").is_dir() else workspace_root
    for current_root, dir_names, file_names in os.walk(scan_root):
        dir_names[:] = [name for name in dir_names if name not in IGNORED_DIR_NAMES]
        current_path = Path(current_root)
        for file_name in file_names:
            if Path(file_name).suffix not in SUPPORTED_SCRIPT_EXTENSIONS:
                continue
            files.append(current_path / file_name)
    return files


class _PythonEntityExtractor:
    def __init__(self, workspace_root: Path, file_path: Path) -> None:
        self.workspace_root = workspace_root
        self.file_path = file_path
        self.entities: list[ObservedEntity] = []
        self.relations: list[ObservedRelation] = []

    def extract(self) -> None:
        source = self.file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(self.file_path))
        relative_path = self.file_path.relative_to(self.workspace_root).as_posix()
        module_name = _module_name_for_path(relative_path)
        module_entity = ObservedEntity(
            language="python",
            entity_type="module",
            canonical_name=module_name,
            file_path=relative_path,
            signature=None,
            start_line=1,
            end_line=len(source.splitlines()) or 1,
            stable_hash=_stable_hash(tree),
        )
        self.entities.append(module_entity)
        top_level_functions: dict[str, str] = {}
        class_methods: dict[str, set[str]] = {}
        pending_calls: list[tuple[str, str, str, float]] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_canonical = f"{module_name}.{node.name}"
                class_methods[class_canonical] = set()
                self.entities.append(
                    ObservedEntity(
                        language="python",
                        entity_type="class",
                        canonical_name=class_canonical,
                        file_path=relative_path,
                        signature=_class_signature(node),
                        start_line=getattr(node, "lineno", None),
                        end_line=getattr(node, "end_lineno", None),
                        stable_hash=_stable_hash(node),
                    )
                )
                self.relations.append(
                    ObservedRelation(
                        from_canonical_name=module_name,
                        to_canonical_name=class_canonical,
                        relation_type="contains",
                        source="ast_exact",
                        confidence=1.0,
                    )
                )
                for child in node.body:
                    if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    method_canonical = f"{class_canonical}.{child.name}"
                    class_methods[class_canonical].add(child.name)
                    self.entities.append(
                        ObservedEntity(
                            language="python",
                            entity_type="method",
                            canonical_name=method_canonical,
                            file_path=relative_path,
                            signature=_function_signature(child),
                            start_line=getattr(child, "lineno", None),
                            end_line=getattr(child, "end_lineno", None),
                            stable_hash=_stable_hash(child),
                        )
                    )
                    self.relations.append(
                        ObservedRelation(
                            from_canonical_name=class_canonical,
                            to_canonical_name=method_canonical,
                            relation_type="contains",
                            source="ast_exact",
                            confidence=1.0,
                        )
                    )
                    pending_calls.extend(_collect_calls(method_canonical, child, module_name, class_canonical))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_canonical = f"{module_name}.{node.name}"
                top_level_functions[node.name] = function_canonical
                self.entities.append(
                    ObservedEntity(
                        language="python",
                        entity_type="function",
                        canonical_name=function_canonical,
                        file_path=relative_path,
                        signature=_function_signature(node),
                        start_line=getattr(node, "lineno", None),
                        end_line=getattr(node, "end_lineno", None),
                        stable_hash=_stable_hash(node),
                    )
                )
                self.relations.append(
                    ObservedRelation(
                        from_canonical_name=module_name,
                        to_canonical_name=function_canonical,
                        relation_type="contains",
                        source="ast_exact",
                        confidence=1.0,
                    )
                )
                pending_calls.extend(_collect_calls(function_canonical, node, module_name, None))
        top_level_names = set(top_level_functions)
        class_method_names = {class_name: set(methods) for class_name, methods in class_methods.items()}
        for from_name, raw_target, current_class, confidence in pending_calls:
            resolved = _resolve_call_target(raw_target, module_name, current_class, top_level_names, class_method_names)
            if resolved is None:
                continue
            self.relations.append(
                ObservedRelation(
                    from_canonical_name=from_name,
                    to_canonical_name=resolved,
                    relation_type="calls",
                    source="ast_exact" if confidence >= 1.0 else "ast_inferred",
                    confidence=confidence,
                )
            )


class _ScriptEntityExtractor:
    CLASS_PATTERN = re.compile(r"(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)[^{]*\{")
    FUNCTION_PATTERN = re.compile(r"(?m)^\s*(?:export\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*\{")
    ARROW_PATTERN = re.compile(r"(?m)^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>\s*\{")
    METHOD_PATTERN = re.compile(r"(?m)^\s*(?:async\s+)?([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*\{")

    def __init__(self, workspace_root: Path, file_path: Path) -> None:
        self.workspace_root = workspace_root
        self.file_path = file_path
        self.entities: list[ObservedEntity] = []
        self.relations: list[ObservedRelation] = []

    def extract(self) -> None:
        source = self.file_path.read_text(encoding="utf-8")
        relative_path = self.file_path.relative_to(self.workspace_root).as_posix()
        module_name = _module_name_for_path(relative_path)
        language = _language_for_path(relative_path)
        self.entities.append(
            ObservedEntity(
                language=language,
                entity_type="module",
                canonical_name=module_name,
                file_path=relative_path,
                signature=None,
                start_line=1,
                end_line=len(source.splitlines()) or 1,
                stable_hash=_stable_text_hash(_normalize_js_source(source)),
            )
        )
        top_level_functions: dict[str, str] = {}
        class_methods: dict[str, set[str]] = {}
        class_spans: list[tuple[int, int]] = []
        pending_calls: list[tuple[str, str, str | None, float]] = []

        for match in self.CLASS_PATTERN.finditer(source):
            class_name = match.group(1)
            body_start = match.end() - 1
            body_end = _find_matching_brace(source, body_start)
            class_spans.append((match.start(), body_end))
            class_canonical = f"{module_name}.{class_name}"
            class_block = source[match.start() : body_end + 1]
            class_methods[class_canonical] = set()
            self.entities.append(
                ObservedEntity(
                    language=language,
                    entity_type="class",
                    canonical_name=class_canonical,
                    file_path=relative_path,
                    signature=_js_class_signature(class_block),
                    start_line=_line_number_for_offset(source, match.start()),
                    end_line=_line_number_for_offset(source, body_end),
                    stable_hash=_stable_text_hash(_normalize_js_entity_source(class_block, kind="class", name=class_name)),
                )
            )
            self.relations.append(
                    ObservedRelation(
                        from_canonical_name=module_name,
                        to_canonical_name=class_canonical,
                        relation_type="contains",
                        source="ast_exact",
                        confidence=1.0,
                    )
                )

            class_body = source[body_start + 1 : body_end]
            class_body_offset = body_start + 1
            for method_match in self.METHOD_PATTERN.finditer(class_body):
                method_name = method_match.group(1)
                if method_name == "constructor":
                    continue
                method_body_start = class_body_offset + method_match.end() - 1
                method_body_end = _find_matching_brace(source, method_body_start)
                method_block = source[class_body_offset + method_match.start() : method_body_end + 1]
                method_canonical = f"{class_canonical}.{method_name}"
                class_methods[class_canonical].add(method_name)
                self.entities.append(
                    ObservedEntity(
                        language=language,
                        entity_type="method",
                        canonical_name=method_canonical,
                        file_path=relative_path,
                        signature=_js_callable_signature(method_match.group(2)),
                        start_line=_line_number_for_offset(source, class_body_offset + method_match.start()),
                        end_line=_line_number_for_offset(source, method_body_end),
                        stable_hash=_stable_text_hash(_normalize_js_entity_source(method_block, kind="method", name=method_name)),
                    )
                )
                self.relations.append(
                    ObservedRelation(
                        from_canonical_name=class_canonical,
                        to_canonical_name=method_canonical,
                        relation_type="contains",
                        source="ast_exact",
                        confidence=1.0,
                    )
                )
                pending_calls.extend(_collect_script_calls(method_canonical, method_block, module_name, class_canonical))

        for pattern in (self.FUNCTION_PATTERN, self.ARROW_PATTERN):
            for match in pattern.finditer(source):
                if any(start <= match.start() <= end for start, end in class_spans):
                    continue
                function_name = match.group(1)
                function_canonical = f"{module_name}.{function_name}"
                body_start = match.end() - 1
                body_end = _find_matching_brace(source, body_start)
                function_block = source[match.start() : body_end + 1]
                top_level_functions[function_name] = function_canonical
                self.entities.append(
                    ObservedEntity(
                        language=language,
                        entity_type="function",
                        canonical_name=function_canonical,
                        file_path=relative_path,
                        signature=_js_callable_signature(match.group(2)),
                        start_line=_line_number_for_offset(source, match.start()),
                        end_line=_line_number_for_offset(source, body_end),
                        stable_hash=_stable_text_hash(
                            _normalize_js_entity_source(
                                function_block,
                                kind="arrow_function" if pattern is self.ARROW_PATTERN else "function",
                                name=function_name,
                            )
                        ),
                    )
                )
                self.relations.append(
                    ObservedRelation(
                        from_canonical_name=module_name,
                        to_canonical_name=function_canonical,
                        relation_type="contains",
                        source="ast_exact",
                        confidence=1.0,
                    )
                )
                pending_calls.extend(_collect_script_calls(function_canonical, function_block, module_name, None))

        top_level_names = set(top_level_functions)
        for from_name, raw_target, current_class, confidence in pending_calls:
            resolved = _resolve_call_target(raw_target, module_name, current_class, top_level_names, class_methods)
            if resolved is None:
                continue
            self.relations.append(
                ObservedRelation(
                    from_canonical_name=from_name,
                    to_canonical_name=resolved,
                    relation_type="calls",
                    source="ast_exact" if confidence >= 1.0 else "ast_inferred",
                    confidence=confidence,
                )
            )


def _collect_calls(
    source_canonical_name: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_name: str,
    current_class: str | None,
) -> list[tuple[str, str, str | None, float]]:
    calls: list[tuple[str, str, str | None, float]] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        target_name, confidence = _call_target_name(child)
        if target_name is None:
            continue
        calls.append((source_canonical_name, target_name, current_class, confidence))
    return calls


def _call_target_name(node: ast.Call) -> tuple[str | None, float]:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id, 1.0
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
        return func.attr, 1.0
    if isinstance(func, ast.Attribute):
        return func.attr, 0.6
    return None, 0.0


def _resolve_call_target(
    raw_target: str,
    module_name: str,
    current_class: str | None,
    top_level_names: set[str],
    class_method_names: dict[str, set[str]],
) -> str | None:
    if current_class is not None and raw_target in class_method_names.get(current_class, set()):
        return f"{current_class}.{raw_target}"
    if raw_target in top_level_names:
        return f"{module_name}.{raw_target}"
    candidates = [f"{class_name}.{raw_target}" for class_name, method_names in class_method_names.items() if raw_target in method_names]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _module_name_for_path(relative_path: str) -> str:
    path = Path(relative_path)
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _language_for_path(file_path: str | None) -> str:
    if file_path is None:
        return "unknown"
    suffix = Path(file_path).suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".js", ".jsx"}:
        return "javascript"
    if suffix in {".ts", ".tsx"}:
        return "typescript"
    return "unknown"


def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    positional = [arg.arg for arg in list(node.args.posonlyargs) + list(node.args.args)]
    keyword_only = [arg.arg for arg in node.args.kwonlyargs]
    parts = positional + (["*" + name for name in keyword_only] if keyword_only else [])
    if node.args.vararg is not None:
        parts.append("*" + node.args.vararg.arg)
    if node.args.kwarg is not None:
        parts.append("**" + node.args.kwarg.arg)
    returns = None if node.returns is None else ast.unparse(node.returns)
    return f"({', '.join(parts)}) -> {returns or 'None'}"


def _class_signature(node: ast.ClassDef) -> str:
    bases = [ast.unparse(base) for base in node.bases] or ["object"]
    return f"({', '.join(bases)})"


def _stable_hash(node: ast.AST) -> str:
    normalized = ast.dump(_normalize_for_hash(node), annotate_fields=True, include_attributes=False)
    return sha256(normalized.encode("utf-8")).hexdigest()


def _stable_text_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _normalize_for_hash(node: ast.AST) -> ast.AST:
    node_copy = ast.fix_missing_locations(ast.parse(ast.unparse(node)).body[0] if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else ast.parse(ast.unparse(node)))
    if isinstance(node_copy, ast.Module):
        return node_copy
    if isinstance(node_copy, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        node_copy.name = "_"
    return node_copy


def _normalize_js_source(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"//.*$", "", source, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", source).strip()


def _normalize_js_entity_source(source: str, *, kind: str, name: str) -> str:
    normalized = _normalize_js_source(source)
    if kind == "class":
        return re.sub(rf"\bclass\s+{re.escape(name)}\b", "class _", normalized, count=1)
    if kind == "function":
        return re.sub(rf"\bfunction\s+{re.escape(name)}\b", "function _", normalized, count=1)
    if kind == "arrow_function":
        return re.sub(rf"\b(const|let|var)\s+{re.escape(name)}\s*=", r"\1 _ =", normalized, count=1)
    if kind == "method":
        normalized = re.sub(rf"^\s*async\s+{re.escape(name)}\s*\(", "async _(", normalized, count=1)
        return re.sub(rf"^\s*{re.escape(name)}\s*\(", "_(", normalized, count=1)
    return normalized


def _find_matching_brace(source: str, open_index: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_backtick = False
    escape = False
    for index in range(open_index, len(source)):
        char = source[index]
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if in_single:
            if char == "'":
                in_single = False
            continue
        if in_double:
            if char == '"':
                in_double = False
            continue
        if in_backtick:
            if char == "`":
                in_backtick = False
            continue
        if char == "'":
            in_single = True
            continue
        if char == '"':
            in_double = True
            continue
        if char == "`":
            in_backtick = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise DaemonConflictError("unbalanced braces in script provenance extraction")


def _line_number_for_offset(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _js_callable_signature(params: str) -> str:
    normalized = ", ".join(part.strip() for part in params.split(",") if part.strip())
    return f"({normalized}) -> unknown"


def _js_class_signature(class_block: str) -> str:
    match = re.search(r"\bextends\s+([A-Za-z_$][\w$]*)", class_block)
    return f"({match.group(1) if match else 'object'})"


def _collect_script_calls(
    source_canonical_name: str,
    block: str,
    module_name: str,
    current_class: str | None,
) -> list[tuple[str, str, str | None, float]]:
    calls: list[tuple[str, str, str | None, float]] = []
    seen: set[tuple[str, float]] = set()
    for target in re.findall(r"\bthis\.([A-Za-z_$][\w$]*)\s*\(", block):
        key = (target, 1.0)
        if key not in seen:
            seen.add(key)
            calls.append((source_canonical_name, target, current_class, 1.0))
    for target in re.findall(r"(?<!\.)\b([A-Za-z_$][\w$]*)\s*\(", block):
        if target in JS_KEYWORD_CALL_NAMES:
            continue
        key = (target, 1.0)
        if key not in seen:
            seen.add(key)
            calls.append((source_canonical_name, target, current_class, 1.0))
    for target in re.findall(r"\.([A-Za-z_$][\w$]*)\s*\(", block):
        if target in JS_KEYWORD_CALL_NAMES:
            continue
        key = (target, 0.6)
        if key not in seen:
            seen.add(key)
            calls.append((source_canonical_name, target, current_class, 0.6))
    return calls


def _latest_prompt_row(session: Session, node_version_id: UUID) -> PromptRecord | None:
    return session.execute(
        select(PromptRecord).where(PromptRecord.node_version_id == node_version_id).order_by(PromptRecord.delivered_at.desc(), PromptRecord.id.desc())
    ).scalars().first()


def _latest_summary_row(session: Session, node_version_id: UUID, *, include_provenance: bool = False) -> SummaryRecord | None:
    statement = select(SummaryRecord).where(SummaryRecord.node_version_id == node_version_id)
    if not include_provenance:
        statement = statement.where(SummaryRecord.summary_type != "provenance")
    return session.execute(statement.order_by(SummaryRecord.created_at.desc(), SummaryRecord.id.desc())).scalars().first()


def _build_rationale_summary(version: NodeVersion, prompt_row: PromptRecord | None, summary_row: SummaryRecord | None) -> str:
    pieces = [f"Node '{version.title}' prompt: {version.prompt.strip()}"]
    if prompt_row is not None and prompt_row.content.strip():
        pieces.append(f"Latest delivered prompt: {prompt_row.content.strip()}")
    if summary_row is not None and summary_row.content.strip():
        pieces.append(f"Latest summary ({summary_row.summary_type}): {summary_row.content.strip()}")
    return " | ".join(piece[:240] for piece in pieces)


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _history_rows_for_version(session: Session, node_version_id: UUID) -> list[NodeEntityChange]:
    return session.execute(
        select(NodeEntityChange).where(NodeEntityChange.node_version_id == node_version_id).order_by(NodeEntityChange.created_at, NodeEntityChange.id)
    ).scalars().all()


def _entity_history_query(session: Session, *, canonical_name: str, changed_only: bool) -> list[NodeEntityChange]:
    statement = (
        select(NodeEntityChange)
        .join(CodeEntity, CodeEntity.id == NodeEntityChange.entity_id)
        .where(or_(CodeEntity.canonical_name == canonical_name, NodeEntityChange.observed_canonical_name == canonical_name))
        .order_by(NodeEntityChange.created_at, NodeEntityChange.id)
    )
    rows = session.execute(statement).scalars().all()
    if changed_only:
        rows = [row for row in rows if row.change_type in CHANGED_ENTITY_TYPES]
    return rows


def _count_change_types(rows: list[NodeEntityChange]) -> dict[str, int]:
    counts = {"added": 0, "modified": 0, "unchanged": 0, "renamed_or_moved": 0, "removed": 0}
    for row in rows:
        counts[row.change_type] = counts.get(row.change_type, 0) + 1
    return counts


def _entity_snapshot(row: CodeEntity) -> EntitySnapshot:
    return EntitySnapshot(
        id=row.id,
        entity_type=row.entity_type,
        canonical_name=row.canonical_name,
        file_path=row.file_path,
        signature=row.signature,
        start_line=row.start_line,
        end_line=row.end_line,
        stable_hash=row.stable_hash,
        created_at=row.created_at.astimezone(timezone.utc).isoformat(),
        updated_at=row.updated_at.astimezone(timezone.utc).isoformat(),
    )


def _history_snapshot(session: Session, row: NodeEntityChange) -> EntityHistoryEntrySnapshot:
    version = session.get(NodeVersion, row.node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return EntityHistoryEntrySnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        logical_node_id=version.logical_node_id,
        entity_id=row.entity_id,
        prompt_record_id=row.prompt_record_id,
        summary_record_id=row.summary_record_id,
        change_type=row.change_type,
        match_confidence=row.match_confidence,
        match_reason=row.match_reason,
        rationale_summary=row.rationale_summary,
        observed_canonical_name=row.observed_canonical_name,
        observed_file_path=row.observed_file_path,
        observed_signature=row.observed_signature,
        observed_stable_hash=row.observed_stable_hash,
        metadata_json=dict(row.metadata_json or {}),
        created_at=row.created_at.astimezone(timezone.utc).isoformat(),
    )


def _relation_snapshot(row: CodeRelation, from_name: str, to_name: str) -> EntityRelationSnapshot:
    return EntityRelationSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        from_entity_id=row.from_entity_id,
        from_canonical_name=from_name,
        to_entity_id=row.to_entity_id,
        to_canonical_name=to_name,
        relation_type=row.relation_type,
        source=row.source,
        confidence=row.confidence,
        rationale_summary=row.rationale_summary,
        created_at=row.created_at.astimezone(timezone.utc).isoformat(),
    )
