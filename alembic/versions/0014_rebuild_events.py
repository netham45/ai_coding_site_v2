"""create rebuild event history table

Revision ID: 0014_rebuild_events
Revises: 0013_merge_conflict_records
Create Date: 2026-03-09 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0014_rebuild_events"
down_revision = "0013_merge_conflict_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rebuild_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("root_logical_node_id", sa.Uuid(), nullable=False),
        sa.Column("root_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("target_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("event_kind", sa.String(length=64), nullable=False),
        sa.Column("event_status", sa.String(length=64), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("trigger_reason", sa.String(length=128), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["root_logical_node_id"], ["hierarchy_nodes.node_id"]),
        sa.ForeignKeyConstraint(["root_node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["target_node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rebuild_events_root_logical_node_id"), "rebuild_events", ["root_logical_node_id"], unique=False)
    op.create_index(op.f("ix_rebuild_events_root_node_version_id"), "rebuild_events", ["root_node_version_id"], unique=False)
    op.create_index(op.f("ix_rebuild_events_target_node_version_id"), "rebuild_events", ["target_node_version_id"], unique=False)
    op.create_index(op.f("ix_rebuild_events_event_kind"), "rebuild_events", ["event_kind"], unique=False)
    op.create_index(op.f("ix_rebuild_events_event_status"), "rebuild_events", ["event_status"], unique=False)
    op.create_index(op.f("ix_rebuild_events_scope"), "rebuild_events", ["scope"], unique=False)
    op.create_index(op.f("ix_rebuild_events_created_at"), "rebuild_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rebuild_events_created_at"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_scope"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_event_status"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_event_kind"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_target_node_version_id"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_root_node_version_id"), table_name="rebuild_events")
    op.drop_index(op.f("ix_rebuild_events_root_logical_node_id"), table_name="rebuild_events")
    op.drop_table("rebuild_events")
