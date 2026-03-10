"""create workflow events table

Revision ID: 0018_workflow_events
Revises: 0017_test_results
Create Date: 2026-03-09 01:15:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0018_workflow_events"
down_revision = "0017_test_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("logical_node_id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=True),
        sa.Column("node_run_id", sa.Uuid(), nullable=True),
        sa.Column("event_scope", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["logical_node_id"], ["hierarchy_nodes.node_id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_events_logical_node_id", "workflow_events", ["logical_node_id"])
    op.create_index("ix_workflow_events_node_version_id", "workflow_events", ["node_version_id"])
    op.create_index("ix_workflow_events_node_run_id", "workflow_events", ["node_run_id"])
    op.create_index("ix_workflow_events_event_scope", "workflow_events", ["event_scope"])
    op.create_index("ix_workflow_events_event_type", "workflow_events", ["event_type"])
    op.create_index("ix_workflow_events_created_at", "workflow_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_workflow_events_created_at", table_name="workflow_events")
    op.drop_index("ix_workflow_events_event_type", table_name="workflow_events")
    op.drop_index("ix_workflow_events_event_scope", table_name="workflow_events")
    op.drop_index("ix_workflow_events_node_run_id", table_name="workflow_events")
    op.drop_index("ix_workflow_events_node_version_id", table_name="workflow_events")
    op.drop_index("ix_workflow_events_logical_node_id", table_name="workflow_events")
    op.drop_table("workflow_events")
