"""create daemon authority state and mutation event tables

Revision ID: 0002_daemon_authority_records
Revises: 0001_bootstrap_metadata
Create Date: 2026-03-08 00:15:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_daemon_authority_records"
down_revision = "0001_bootstrap_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daemon_node_states",
        sa.Column("node_id", sa.String(length=255), primary_key=True, nullable=False),
        sa.Column("current_run_id", sa.Uuid(), nullable=True),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False),
        sa.Column("authority", sa.String(length=32), nullable=False),
        sa.Column("last_command", sa.String(length=64), nullable=False),
        sa.Column("last_event_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("lifecycle_state in ('active','paused')", name="ck_daemon_node_states_lifecycle_state"),
        sa.CheckConstraint("authority = 'daemon'", name="ck_daemon_node_states_authority"),
        sa.CheckConstraint(
            "last_command in ('node.run.start','node.pause','node.resume')",
            name="ck_daemon_node_states_last_command",
        ),
    )
    op.create_table(
        "daemon_mutation_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("node_id", sa.String(length=255), nullable=False),
        sa.Column("command", sa.String(length=64), nullable=False),
        sa.Column("previous_state", sa.String(length=32), nullable=True),
        sa.Column("resulting_state", sa.String(length=32), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "command in ('node.run.start','node.pause','node.resume')",
            name="ck_daemon_mutation_events_command",
        ),
        sa.CheckConstraint(
            "resulting_state in ('active','paused')",
            name="ck_daemon_mutation_events_resulting_state",
        ),
    )
    op.create_index("ix_daemon_mutation_events_node_id", "daemon_mutation_events", ["node_id"])
    op.execute(
        sa.text(
            """
            create view daemon_active_node_runs as
            select
                node_id,
                current_run_id,
                lifecycle_state,
                authority,
                last_command,
                last_event_id,
                updated_at
            from daemon_node_states
            where current_run_id is not null
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("drop view if exists daemon_active_node_runs"))
    op.drop_index("ix_daemon_mutation_events_node_id", table_name="daemon_mutation_events")
    op.drop_table("daemon_mutation_events")
    op.drop_table("daemon_node_states")
