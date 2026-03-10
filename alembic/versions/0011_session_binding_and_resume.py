"""create durable session binding tables

Revision ID: 0011_session_binding_and_resume
Revises: 0010_node_run_orchestration
Create Date: 2026-03-09 11:20:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0011_session_binding_and_resume"
down_revision = "0010_node_run_orchestration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("node_run_id", sa.Uuid(), nullable=True),
        sa.Column("session_role", sa.String(length=32), nullable=False),
        sa.Column("parent_session_id", sa.Uuid(), nullable=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_session_id", sa.String(length=255), nullable=True),
        sa.Column("tmux_session_name", sa.String(length=255), nullable=True),
        sa.Column("cwd", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["parent_session_id"], ["sessions.id"]),
        sa.CheckConstraint(
            "(session_role = 'primary' and parent_session_id is null) or "
            "(session_role = 'pushed_child' and parent_session_id is not null)",
            name="ck_sessions_role_parent",
        ),
    )
    op.create_index("ix_sessions_node_version_id", "sessions", ["node_version_id"])
    op.create_index("ix_sessions_node_run_id", "sessions", ["node_run_id"])
    op.create_index("ix_sessions_session_role", "sessions", ["session_role"])
    op.create_index("ix_sessions_provider_session_id", "sessions", ["provider_session_id"])
    op.create_index("ix_sessions_tmux_session_name", "sessions", ["tmux_session_name"])
    op.create_index("ix_sessions_status", "sessions", ["status"])
    op.create_index("ix_sessions_parent_session_id", "sessions", ["parent_session_id"])

    op.create_table(
        "session_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
    )
    op.create_index("ix_session_events_session_id", "session_events", ["session_id"])
    op.create_index("ix_session_events_event_type", "session_events", ["event_type"])
    op.create_index("ix_session_events_created_at", "session_events", ["created_at"])

    op.create_table(
        "child_session_results",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("child_session_id", sa.Uuid(), nullable=False),
        sa.Column("parent_compiled_subtask_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["parent_compiled_subtask_id"], ["compiled_subtasks.id"]),
    )
    op.create_index("ix_child_session_results_child_session_id", "child_session_results", ["child_session_id"])
    op.create_index(
        "ix_child_session_results_parent_compiled_subtask_id",
        "child_session_results",
        ["parent_compiled_subtask_id"],
    )
    op.create_index("ix_child_session_results_status", "child_session_results", ["status"])


def downgrade() -> None:
    op.drop_index("ix_child_session_results_status", table_name="child_session_results")
    op.drop_index("ix_child_session_results_parent_compiled_subtask_id", table_name="child_session_results")
    op.drop_index("ix_child_session_results_child_session_id", table_name="child_session_results")
    op.drop_table("child_session_results")

    op.drop_index("ix_session_events_created_at", table_name="session_events")
    op.drop_index("ix_session_events_event_type", table_name="session_events")
    op.drop_index("ix_session_events_session_id", table_name="session_events")
    op.drop_table("session_events")

    op.drop_index("ix_sessions_parent_session_id", table_name="sessions")
    op.drop_index("ix_sessions_status", table_name="sessions")
    op.drop_index("ix_sessions_tmux_session_name", table_name="sessions")
    op.drop_index("ix_sessions_provider_session_id", table_name="sessions")
    op.drop_index("ix_sessions_session_role", table_name="sessions")
    op.drop_index("ix_sessions_node_run_id", table_name="sessions")
    op.drop_index("ix_sessions_node_version_id", table_name="sessions")
    op.drop_table("sessions")
