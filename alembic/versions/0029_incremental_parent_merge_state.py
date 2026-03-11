"""add incremental parent merge durable state

Revision ID: 0029_incr_parent_merge_state
Revises: 0028_subtask_execution_results
Create Date: 2026-03-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0029_incr_parent_merge_state"
down_revision = "0028_subtask_execution_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parent_incremental_merge_lanes",
        sa.Column("parent_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_parent_head_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("last_successful_merge_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("blocked_reason", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("parent_node_version_id"),
    )
    op.create_index(
        "ix_parent_incremental_merge_lanes_status",
        "parent_incremental_merge_lanes",
        ["status"],
        unique=False,
    )

    op.create_table(
        "incremental_child_merge_state",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("child_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("child_final_commit_sha", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("applied_merge_order", sa.Integer(), nullable=True),
        sa.Column("parent_commit_before", sa.String(length=64), nullable=True),
        sa.Column("parent_commit_after", sa.String(length=64), nullable=True),
        sa.Column("conflict_id", sa.Uuid(), sa.ForeignKey("merge_conflicts.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("parent_node_version_id", "child_node_version_id", name="uq_incremental_child_merge_state_pair"),
    )
    op.create_index(
        "ix_incremental_child_merge_state_parent_status_created",
        "incremental_child_merge_state",
        ["parent_node_version_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_incremental_child_merge_state_parent_node_version_id",
        "incremental_child_merge_state",
        ["parent_node_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_incremental_child_merge_state_child_node_version_id",
        "incremental_child_merge_state",
        ["child_node_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_incremental_child_merge_state_status",
        "incremental_child_merge_state",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_incremental_child_merge_state_conflict_id",
        "incremental_child_merge_state",
        ["conflict_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_incremental_child_merge_state_conflict_id", table_name="incremental_child_merge_state")
    op.drop_index("ix_incremental_child_merge_state_status", table_name="incremental_child_merge_state")
    op.drop_index("ix_incremental_child_merge_state_child_node_version_id", table_name="incremental_child_merge_state")
    op.drop_index("ix_incremental_child_merge_state_parent_node_version_id", table_name="incremental_child_merge_state")
    op.drop_index("ix_incremental_child_merge_state_parent_status_created", table_name="incremental_child_merge_state")
    op.drop_table("incremental_child_merge_state")
    op.drop_index("ix_parent_incremental_merge_lanes_status", table_name="parent_incremental_merge_lanes")
    op.drop_table("parent_incremental_merge_lanes")
