"""create prompt and summary history tables

Revision ID: 0020_prompt_and_summary_history
Revises: 0019_parent_failure_counters
Create Date: 2026-03-09 15:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0020_prompt_and_summary_history"
down_revision = "0019_parent_failure_counters"
branch_labels = None
depends_on = None


PROMPT_ROLES = (
    "main_prompt",
    "subtask_prompt",
    "pause_summary_prompt",
    "review_prompt",
    "testing_prompt",
    "docs_prompt",
    "system_prompt",
)

SUMMARY_TYPES = (
    "subtask",
    "failure",
    "pause",
    "node",
    "review",
    "testing",
    "validation",
    "rectification",
    "parent_replan",
    "parent_child_failure_pause",
    "docs",
    "provenance",
)

SUMMARY_SCOPES = (
    "subtask_attempt",
    "node_run",
    "node_version",
    "pause",
    "parent_decision",
)


def upgrade() -> None:
    op.create_table(
        "prompts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("node_run_id", sa.Uuid(), nullable=False),
        sa.Column("compiled_subtask_id", sa.Uuid(), nullable=True),
        sa.Column("prompt_role", sa.String(length=64), nullable=False),
        sa.Column("source_subtask_key", sa.String(length=128), nullable=True),
        sa.Column("template_path", sa.String(length=255), nullable=True),
        sa.Column("template_hash", sa.String(length=64), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "prompt_role in ('main_prompt','subtask_prompt','pause_summary_prompt','review_prompt','testing_prompt','docs_prompt','system_prompt')",
            name="ck_prompts_prompt_role",
        ),
    )
    op.create_index("ix_prompts_node_version_id", "prompts", ["node_version_id"])
    op.create_index("ix_prompts_node_run_id", "prompts", ["node_run_id"])
    op.create_index("ix_prompts_compiled_subtask_id", "prompts", ["compiled_subtask_id"])
    op.create_index("ix_prompts_prompt_role", "prompts", ["prompt_role"])
    op.create_index("ix_prompts_content_hash", "prompts", ["content_hash"])
    op.create_index("ix_prompts_delivered_at", "prompts", ["delivered_at"])

    op.create_table(
        "summaries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("node_run_id", sa.Uuid(), nullable=True),
        sa.Column("compiled_subtask_id", sa.Uuid(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=True),
        sa.Column("summary_type", sa.String(length=64), nullable=False),
        sa.Column("summary_scope", sa.String(length=32), nullable=False),
        sa.Column("summary_path", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "summary_type in ('subtask','failure','pause','node','review','testing','validation','rectification','parent_replan','parent_child_failure_pause','docs','provenance')",
            name="ck_summaries_summary_type",
        ),
        sa.CheckConstraint(
            "summary_scope in ('subtask_attempt','node_run','node_version','pause','parent_decision')",
            name="ck_summaries_summary_scope",
        ),
        sa.CheckConstraint("attempt_number is null or attempt_number > 0", name="ck_summaries_attempt_number"),
    )
    op.create_index("ix_summaries_node_version_id", "summaries", ["node_version_id"])
    op.create_index("ix_summaries_node_run_id", "summaries", ["node_run_id"])
    op.create_index("ix_summaries_compiled_subtask_id", "summaries", ["compiled_subtask_id"])
    op.create_index("ix_summaries_summary_type", "summaries", ["summary_type"])
    op.create_index("ix_summaries_summary_scope", "summaries", ["summary_scope"])
    op.create_index("ix_summaries_content_hash", "summaries", ["content_hash"])
    op.create_index("ix_summaries_created_at", "summaries", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_summaries_created_at", table_name="summaries")
    op.drop_index("ix_summaries_content_hash", table_name="summaries")
    op.drop_index("ix_summaries_summary_scope", table_name="summaries")
    op.drop_index("ix_summaries_summary_type", table_name="summaries")
    op.drop_index("ix_summaries_compiled_subtask_id", table_name="summaries")
    op.drop_index("ix_summaries_node_run_id", table_name="summaries")
    op.drop_index("ix_summaries_node_version_id", table_name="summaries")
    op.drop_table("summaries")

    op.drop_index("ix_prompts_delivered_at", table_name="prompts")
    op.drop_index("ix_prompts_content_hash", table_name="prompts")
    op.drop_index("ix_prompts_prompt_role", table_name="prompts")
    op.drop_index("ix_prompts_compiled_subtask_id", table_name="prompts")
    op.drop_index("ix_prompts_node_run_id", table_name="prompts")
    op.drop_index("ix_prompts_node_version_id", table_name="prompts")
    op.drop_table("prompts")
