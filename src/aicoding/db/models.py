from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from aicoding.db.base import Base


class BootstrapMetadata(Base):
    __tablename__ = "bootstrap_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DaemonNodeState(Base):
    __tablename__ = "daemon_node_states"

    node_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, index=True)
    current_run_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False)
    authority: Mapped[str] = mapped_column(String(32), nullable=False, default="daemon")
    last_command: Mapped[str] = mapped_column(String(64), nullable=False)
    last_event_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DaemonMutationEvent(Base):
    __tablename__ = "daemon_mutation_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    command: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resulting_state: Mapped[str] = mapped_column(String(32), nullable=False)
    run_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NodeHierarchyDefinition(Base):
    __tablename__ = "node_hierarchy_definitions"

    kind: Mapped[str] = mapped_column(String(100), primary_key=True)
    tier: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    main_prompt: Mapped[str] = mapped_column(String(255), nullable=False)
    entry_task: Mapped[str] = mapped_column(String(100), nullable=False)
    available_tasks_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allow_parentless: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allowed_parent_kinds_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_parent_tiers_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_child_kinds_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_child_tiers_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    min_children: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_children: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class HierarchyNode(Base):
    __tablename__ = "hierarchy_nodes"

    node_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    parent_node_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    created_via: Mapped[str] = mapped_column(String(32), nullable=False)
    max_children: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class YamlSchemaValidationRecord(Base):
    __tablename__ = "yaml_schema_validation_records"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source_group: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    relative_path: Mapped[str] = mapped_column(String(255), nullable=False)
    family: Mapped[str] = mapped_column(String(64), nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    issue_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    issues_json: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class NodeLifecycleState(Base):
    __tablename__ = "node_lifecycle_states"

    node_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, index=True)
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    run_status: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    current_run_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    current_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_subtask_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_subtask_attempt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_completed_subtask_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    execution_cursor_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    failure_count_from_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count_consecutive: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    defer_to_user_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_resumable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pause_flag_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    working_tree_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class NodeVersion(Base):
    __tablename__ = "node_versions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    logical_node_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("hierarchy_nodes.node_id"), nullable=False, index=True)
    parent_node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, index=True)
    tier: Mapped[str] = mapped_column(String(32), nullable=False)
    node_kind: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    compiled_workflow_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_workflows.id"), nullable=True, index=True)
    supersedes_node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, unique=True, index=True)
    active_branch_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    branch_generation_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    final_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LogicalNodeCurrentVersion(Base):
    __tablename__ = "logical_node_current_versions"

    logical_node_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("hierarchy_nodes.node_id"), primary_key=True)
    authoritative_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    latest_created_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source_group: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    relative_path: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_family: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    merge_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="direct")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NodeVersionSourceDocument(Base):
    __tablename__ = "node_version_source_documents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    source_document_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("source_documents.id"), nullable=False, index=True)
    source_role: Mapped[str] = mapped_column(String(64), nullable=False)
    resolution_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_resolved_input: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CompiledWorkflow(Base):
    __tablename__ = "compiled_workflows"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resolved_yaml: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class CompiledWorkflowSource(Base):
    __tablename__ = "compiled_workflow_sources"

    compiled_workflow_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_workflows.id"), primary_key=True)
    source_document_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("source_documents.id"), primary_key=True)
    source_role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)


class CompiledTask(Base):
    __tablename__ = "compiled_tasks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    compiled_workflow_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_workflows.id"), nullable=False, index=True)
    task_key: Mapped[str] = mapped_column(String(128), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CompiledSubtask(Base):
    __tablename__ = "compiled_subtasks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    compiled_workflow_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_workflows.id"), nullable=False, index=True)
    compiled_task_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_tasks.id"), nullable=False, index=True)
    source_subtask_key: Mapped[str] = mapped_column(String(128), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    subtask_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prompt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    command_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    args_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    env_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    environment_policy_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment_request_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    retry_policy_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    block_on_user_flag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pause_summary_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    inserted_by_hook: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    inserted_by_hook_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    source_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CompiledSubtaskDependency(Base):
    __tablename__ = "compiled_subtask_dependencies"

    compiled_subtask_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), primary_key=True)
    depends_on_compiled_subtask_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), primary_key=True)


class NodeRun(Base):
    __tablename__ = "node_runs"
    __table_args__ = (
        UniqueConstraint("node_version_id", "run_number", name="uq_node_runs_version_run_number"),
        CheckConstraint("run_number > 0", name="ck_node_runs_run_number_positive"),
        Index("ix_node_runs_node_version_run_number", "node_version_id", "run_number"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    run_number: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    run_status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    compiled_workflow_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_workflows.id"), nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NodeRunState(Base):
    __tablename__ = "node_run_state"
    __table_args__ = (
        CheckConstraint(
            "current_subtask_attempt is null or current_subtask_attempt > 0",
            name="ck_node_run_state_attempt_positive",
        ),
        CheckConstraint("failure_count_from_children >= 0", name="ck_node_run_state_child_failures_nonnegative"),
        CheckConstraint("failure_count_consecutive >= 0", name="ck_node_run_state_consecutive_failures_nonnegative"),
    )

    node_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_runs.id"), primary_key=True)
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    current_task_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_tasks.id"), nullable=True, index=True)
    current_compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    current_subtask_attempt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_completed_compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True)
    execution_cursor_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    failure_count_from_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count_consecutive: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    defer_to_user_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pause_flag_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    is_resumable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    working_tree_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class NodeRunChildFailureCounter(Base):
    __tablename__ = "node_run_child_failure_counters"
    __table_args__ = (
        CheckConstraint("failure_count >= 0", name="ck_node_run_child_failure_counters_nonnegative"),
    )

    node_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_runs.id"), primary_key=True)
    child_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), primary_key=True)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_failure_class: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    last_failure_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_failure_subtask_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_failed_node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    last_decision_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    last_decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SubtaskAttempt(Base):
    __tablename__ = "subtask_attempts"
    __table_args__ = (
        UniqueConstraint(
            "node_run_id",
            "compiled_subtask_id",
            "attempt_number",
            name="uq_subtask_attempts_identity",
        ),
        CheckConstraint("attempt_number > 0", name="ck_subtask_attempts_attempt_positive"),
        Index(
            "ix_subtask_attempts_run_subtask_attempt",
            "node_run_id",
            "compiled_subtask_id",
            "attempt_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=False, index=True)
    compiled_subtask_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    input_context_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    output_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    execution_result_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    execution_environment_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    changed_files_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    git_head_before: Mapped[str | None] = mapped_column(String(64), nullable=True)
    git_head_after: Mapped[str | None] = mapped_column(String(64), nullable=True)
    validation_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    review_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    testing_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ValidationResult(Base):
    __tablename__ = "validation_results"
    __table_args__ = (
        Index(
            "ix_validation_results_latest_lookup",
            "node_version_id",
            "node_run_id",
            "compiled_subtask_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    check_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    evidence_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class ReviewResult(Base):
    __tablename__ = "review_results"
    __table_args__ = (
        Index(
            "ix_review_results_latest_lookup",
            "node_version_id",
            "node_run_id",
            "compiled_subtask_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    review_definition_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    scope: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    criteria_json: Mapped[list[dict[str, object]] | dict[str, object] | None] = mapped_column(JSON, nullable=True)
    findings_json: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class TestResult(Base):
    __tablename__ = "test_results"
    __table_args__ = (
        Index(
            "ix_test_results_latest_lookup",
            "node_version_id",
            "node_run_id",
            "compiled_subtask_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    testing_definition_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    suite_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    attempt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    results_json: Mapped[dict[str, object] | list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    logical_node_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("hierarchy_nodes.node_id"), nullable=False, index=True)
    node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    event_scope: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class PromptRecord(Base):
    __tablename__ = "prompts"
    __table_args__ = (
        Index("ix_prompts_node_version_delivered", "node_version_id", "delivered_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=False, index=True)
    compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    prompt_role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_subtask_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    template_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    template_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class SummaryRecord(Base):
    __tablename__ = "summaries"
    __table_args__ = (
        Index("ix_summaries_node_version_created", "node_version_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    attempt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    summary_scope: Mapped[str] = mapped_column(String(32), nullable=False, default="subtask_attempt", index=True)
    summary_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "(session_role = 'primary' and parent_session_id is null) "
            "or (session_role = 'pushed_child' and parent_session_id is not null)",
            name="ck_sessions_role_parent_shape",
        ),
        Index("ix_sessions_run_role_status_started", "node_run_id", "session_role", "status", "started_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    node_run_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_runs.id"), nullable=True, index=True)
    session_role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    parent_session_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("sessions.id"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    tmux_session_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    cwd: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SessionEvent(Base):
    __tablename__ = "session_events"
    __table_args__ = (
        Index("ix_session_events_session_created", "session_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    session_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("sessions.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class ChildSessionResult(Base):
    __tablename__ = "child_session_results"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    child_session_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("sessions.id"), nullable=False, index=True)
    parent_compiled_subtask_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("compiled_subtasks.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    result_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NodeChild(Base):
    __tablename__ = "node_children"

    parent_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), primary_key=True)
    child_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), primary_key=True)
    layout_child_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    origin_type: Mapped[str] = mapped_column(String(32), nullable=False, default="layout_generated", index=True)
    ordinal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ParentChildAuthority(Base):
    __tablename__ = "parent_child_authority"

    parent_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), primary_key=True)
    authority_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="layout_authoritative")
    authoritative_layout_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    last_reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ParentIncrementalMergeLane(Base):
    __tablename__ = "parent_incremental_merge_lanes"

    parent_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    current_parent_head_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_successful_merge_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IncrementalChildMergeState(Base):
    __tablename__ = "incremental_child_merge_state"
    __table_args__ = (
        UniqueConstraint("parent_node_version_id", "child_node_version_id", name="uq_incremental_child_merge_state_pair"),
        Index("ix_incremental_child_merge_state_parent_status_created", "parent_node_version_id", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    parent_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    child_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    child_final_commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed_unmerged", index=True)
    applied_merge_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent_commit_before: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parent_commit_after: Mapped[str | None] = mapped_column(String(64), nullable=True)
    conflict_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("merge_conflicts.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class MergeEvent(Base):
    __tablename__ = "merge_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    parent_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    child_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    child_final_commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_commit_before: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_commit_after: Mapped[str] = mapped_column(String(64), nullable=False)
    merge_order: Mapped[int] = mapped_column(Integer, nullable=False)
    had_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MergeConflict(Base):
    __tablename__ = "merge_conflicts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    merge_event_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("merge_events.id"), nullable=False, index=True)
    files_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    merge_base_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RebuildEvent(Base):
    __tablename__ = "rebuild_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    root_logical_node_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("hierarchy_nodes.node_id"), nullable=False, index=True)
    root_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    target_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    event_kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    trigger_reason: Mapped[str] = mapped_column(String(128), nullable=False)
    details_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class NodeDependency(Base):
    __tablename__ = "node_dependencies"
    __table_args__ = (
        UniqueConstraint("node_version_id", "depends_on_node_version_id", name="uq_node_dependencies_pair"),
        CheckConstraint("node_version_id <> depends_on_node_version_id", name="ck_node_dependencies_not_self"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    depends_on_node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    dependency_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    required_state: Mapped[str] = mapped_column(String(32), nullable=False, default="COMPLETE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NodeDependencyBlocker(Base):
    __tablename__ = "node_dependency_blockers"
    __table_args__ = (
        Index("ix_node_dependency_blockers_node_version_created", "node_version_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    dependency_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_dependencies.id"), nullable=True, index=True)
    blocker_kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    target_node_version_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=True, index=True)
    details_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class CompileFailure(Base):
    __tablename__ = "compile_failures"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    failure_stage: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    failure_class: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    target_family: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hook_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class CodeEntity(Base):
    __tablename__ = "code_entities"
    __table_args__ = (
        Index("ix_code_entities_canonical_type_path", "canonical_name", "entity_type", "file_path"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_path: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stable_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class NodeEntityChange(Base):
    __tablename__ = "node_entity_changes"
    __table_args__ = (
        Index("ix_node_entity_changes_version_entity_created", "node_version_id", "entity_id", "created_at"),
        Index("ix_node_entity_changes_entity_created", "entity_id", "created_at"),
        Index("ix_node_entity_changes_observed_name_created", "observed_canonical_name", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("code_entities.id"), nullable=False, index=True)
    prompt_record_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("prompts.id"), nullable=True, index=True)
    summary_record_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("summaries.id"), nullable=True, index=True)
    change_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    match_confidence: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    match_reason: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rationale_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    observed_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observed_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_stable_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class CodeRelation(Base):
    __tablename__ = "code_relations"
    __table_args__ = (
        Index(
            "ix_code_relations_version_from_to_type_created",
            "node_version_id",
            "from_entity_id",
            "to_entity_id",
            "relation_type",
            "created_at",
        ),
        Index("ix_code_relations_from_relation_created", "from_entity_id", "relation_type", "created_at"),
        Index("ix_code_relations_to_relation_created", "to_entity_id", "relation_type", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    from_entity_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("code_entities.id"), nullable=False, index=True)
    to_entity_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("code_entities.id"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class DocumentationOutput(Base):
    __tablename__ = "documentation_outputs"
    __table_args__ = (
        Index("ix_documentation_outputs_node_version_created", "node_version_id", "created_at"),
        Index(
            "ix_documentation_outputs_logical_scope_view_created",
            "logical_node_id",
            "scope",
            "view_name",
            "created_at",
        ),
        Index("ix_documentation_outputs_doc_definition_id", "doc_definition_id"),
        Index("ix_documentation_outputs_content_hash", "content_hash"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    logical_node_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("hierarchy_nodes.node_id"), nullable=False, index=True)
    node_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("node_versions.id"), nullable=False, index=True)
    doc_definition_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    view_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    output_path: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
