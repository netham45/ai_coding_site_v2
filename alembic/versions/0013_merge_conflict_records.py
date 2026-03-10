"""create merge event and conflict tables

Revision ID: 0013_merge_conflict_records
Revises: 0012_child_materialization
Create Date: 2026-03-09 11:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0013_merge_conflict_records"
down_revision = "0012_child_materialization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "merge_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("child_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("child_final_commit_sha", sa.String(length=64), nullable=False),
        sa.Column("parent_commit_before", sa.String(length=64), nullable=False),
        sa.Column("parent_commit_after", sa.String(length=64), nullable=False),
        sa.Column("merge_order", sa.Integer(), nullable=False),
        sa.Column("had_conflict", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["parent_node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("merge_order > 0", name="ck_merge_events_merge_order_positive"),
    )
    op.create_index("ix_merge_events_parent_node_version_id", "merge_events", ["parent_node_version_id"])
    op.create_index("ix_merge_events_child_node_version_id", "merge_events", ["child_node_version_id"])
    op.create_index("ix_merge_events_parent_merge_order", "merge_events", ["parent_node_version_id", "merge_order"])

    op.create_table(
        "merge_conflicts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("merge_event_id", sa.Uuid(), nullable=False),
        sa.Column("files_json", sa.JSON(), nullable=False),
        sa.Column("merge_base_sha", sa.String(length=64), nullable=True),
        sa.Column("resolution_summary", sa.Text(), nullable=True),
        sa.Column("resolution_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merge_event_id"], ["merge_events.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "resolution_status in ('unresolved','resolved','abandoned')",
            name="ck_merge_conflicts_resolution_status",
        ),
    )
    op.create_index("ix_merge_conflicts_merge_event_id", "merge_conflicts", ["merge_event_id"])
    op.create_index("ix_merge_conflicts_resolution_status", "merge_conflicts", ["resolution_status"])


def downgrade() -> None:
    op.drop_index("ix_merge_conflicts_resolution_status", table_name="merge_conflicts")
    op.drop_index("ix_merge_conflicts_merge_event_id", table_name="merge_conflicts")
    op.drop_table("merge_conflicts")
    op.drop_index("ix_merge_events_parent_merge_order", table_name="merge_events")
    op.drop_index("ix_merge_events_child_node_version_id", table_name="merge_events")
    op.drop_index("ix_merge_events_parent_node_version_id", table_name="merge_events")
    op.drop_table("merge_events")
