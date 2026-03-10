"""create immutable workflow compilation tables

Revision ID: 0008_immutable_workflows
Revises: 0007_source_doc_lineage
Create Date: 2026-03-08 06:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0008_immutable_workflows"
down_revision = "0007_source_doc_lineage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "compiled_workflows",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("resolved_yaml", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_compiled_workflows_node_version_id", "compiled_workflows", ["node_version_id"])
    op.create_index("ix_compiled_workflows_source_hash", "compiled_workflows", ["source_hash"])
    op.create_index("ix_compiled_workflows_created_at", "compiled_workflows", ["created_at"])

    op.add_column("node_versions", sa.Column("compiled_workflow_id", sa.Uuid(), nullable=True))
    op.create_index("ix_node_versions_compiled_workflow_id", "node_versions", ["compiled_workflow_id"])
    op.create_foreign_key(
        "fk_node_versions_compiled_workflow_id",
        "node_versions",
        "compiled_workflows",
        ["compiled_workflow_id"],
        ["id"],
    )

    op.create_table(
        "compiled_workflow_sources",
        sa.Column("compiled_workflow_id", sa.Uuid(), sa.ForeignKey("compiled_workflows.id"), nullable=False),
        sa.Column("source_document_id", sa.Uuid(), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("source_role", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("compiled_workflow_id", "source_document_id"),
    )
    op.create_index("ix_compiled_workflow_sources_source_role", "compiled_workflow_sources", ["source_role"])

    op.create_table(
        "compiled_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("compiled_workflow_id", sa.Uuid(), sa.ForeignKey("compiled_workflows.id"), nullable=False),
        sa.Column("task_key", sa.String(length=128), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("compiled_workflow_id", "task_key", name="uq_compiled_tasks_workflow_key"),
        sa.UniqueConstraint("compiled_workflow_id", "ordinal", name="uq_compiled_tasks_workflow_ordinal"),
    )
    op.create_index("ix_compiled_tasks_compiled_workflow_id", "compiled_tasks", ["compiled_workflow_id"])

    op.create_table(
        "compiled_subtasks",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("compiled_workflow_id", sa.Uuid(), sa.ForeignKey("compiled_workflows.id"), nullable=False),
        sa.Column("compiled_task_id", sa.Uuid(), sa.ForeignKey("compiled_tasks.id"), nullable=False),
        sa.Column("source_subtask_key", sa.String(length=128), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("subtask_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("prompt_text", sa.Text(), nullable=True),
        sa.Column("command_text", sa.Text(), nullable=True),
        sa.Column("args_json", sa.JSON(), nullable=True),
        sa.Column("env_json", sa.JSON(), nullable=True),
        sa.Column("retry_policy_json", sa.JSON(), nullable=True),
        sa.Column("block_on_user_flag", sa.String(length=64), nullable=True),
        sa.Column("pause_summary_prompt", sa.Text(), nullable=True),
        sa.Column("inserted_by_hook", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("inserted_by_hook_id", sa.Uuid(), nullable=True),
        sa.Column("source_file_path", sa.String(length=255), nullable=True),
        sa.Column("source_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("compiled_task_id", "ordinal", name="uq_compiled_subtasks_task_ordinal"),
    )
    op.create_index("ix_compiled_subtasks_compiled_workflow_id", "compiled_subtasks", ["compiled_workflow_id"])
    op.create_index("ix_compiled_subtasks_compiled_task_id", "compiled_subtasks", ["compiled_task_id"])
    op.create_index("ix_compiled_subtasks_subtask_type", "compiled_subtasks", ["subtask_type"])

    op.create_table(
        "compiled_subtask_dependencies",
        sa.Column("compiled_subtask_id", sa.Uuid(), sa.ForeignKey("compiled_subtasks.id"), nullable=False),
        sa.Column("depends_on_compiled_subtask_id", sa.Uuid(), sa.ForeignKey("compiled_subtasks.id"), nullable=False),
        sa.CheckConstraint("compiled_subtask_id <> depends_on_compiled_subtask_id", name="ck_compiled_subtask_dependencies_not_self"),
        sa.PrimaryKeyConstraint("compiled_subtask_id", "depends_on_compiled_subtask_id"),
    )

    op.create_table(
        "compile_failures",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("failure_stage", sa.String(length=64), nullable=False),
        sa.Column("failure_class", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=True),
        sa.Column("target_family", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=255), nullable=True),
        sa.Column("hook_id", sa.String(length=255), nullable=True),
        sa.Column("policy_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_compile_failures_node_version_id", "compile_failures", ["node_version_id"])
    op.create_index("ix_compile_failures_failure_stage", "compile_failures", ["failure_stage"])
    op.create_index("ix_compile_failures_failure_class", "compile_failures", ["failure_class"])
    op.create_index("ix_compile_failures_source_hash", "compile_failures", ["source_hash"])
    op.create_index("ix_compile_failures_created_at", "compile_failures", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_compile_failures_created_at", table_name="compile_failures")
    op.drop_index("ix_compile_failures_source_hash", table_name="compile_failures")
    op.drop_index("ix_compile_failures_failure_class", table_name="compile_failures")
    op.drop_index("ix_compile_failures_failure_stage", table_name="compile_failures")
    op.drop_index("ix_compile_failures_node_version_id", table_name="compile_failures")
    op.drop_table("compile_failures")
    op.drop_table("compiled_subtask_dependencies")
    op.drop_index("ix_compiled_subtasks_subtask_type", table_name="compiled_subtasks")
    op.drop_index("ix_compiled_subtasks_compiled_task_id", table_name="compiled_subtasks")
    op.drop_index("ix_compiled_subtasks_compiled_workflow_id", table_name="compiled_subtasks")
    op.drop_table("compiled_subtasks")
    op.drop_index("ix_compiled_tasks_compiled_workflow_id", table_name="compiled_tasks")
    op.drop_table("compiled_tasks")
    op.drop_index("ix_compiled_workflow_sources_source_role", table_name="compiled_workflow_sources")
    op.drop_table("compiled_workflow_sources")
    op.drop_constraint("fk_node_versions_compiled_workflow_id", "node_versions", type_="foreignkey")
    op.drop_index("ix_node_versions_compiled_workflow_id", table_name="node_versions")
    op.drop_column("node_versions", "compiled_workflow_id")
    op.drop_index("ix_compiled_workflows_created_at", table_name="compiled_workflows")
    op.drop_index("ix_compiled_workflows_source_hash", table_name="compiled_workflows")
    op.drop_index("ix_compiled_workflows_node_version_id", table_name="compiled_workflows")
    op.drop_table("compiled_workflows")
