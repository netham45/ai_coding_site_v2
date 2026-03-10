"""create durable node lifecycle state table

Revision ID: 0005_node_lifecycle_state
Revises: 0004_yaml_schema_records
Create Date: 2026-03-08 03:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_node_lifecycle_state"
down_revision = "0004_yaml_schema_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_lifecycle_states",
        sa.Column("node_id", sa.String(length=255), primary_key=True, nullable=False),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False),
        sa.Column("run_status", sa.String(length=16), nullable=True),
        sa.Column("current_run_id", sa.Uuid(), nullable=True),
        sa.Column("current_task_id", sa.String(length=128), nullable=True),
        sa.Column("current_subtask_id", sa.String(length=128), nullable=True),
        sa.Column("current_subtask_attempt", sa.Integer(), nullable=True),
        sa.Column("last_completed_subtask_id", sa.String(length=128), nullable=True),
        sa.Column("execution_cursor_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("failure_count_from_children", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count_consecutive", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("defer_to_user_threshold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_resumable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("pause_flag_name", sa.String(length=64), nullable=True),
        sa.Column("working_tree_state", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_node_lifecycle_states_lifecycle_state", "node_lifecycle_states", ["lifecycle_state"])
    op.create_index("ix_node_lifecycle_states_run_status", "node_lifecycle_states", ["run_status"])
    op.create_index("ix_node_lifecycle_states_current_run_id", "node_lifecycle_states", ["current_run_id"])


def downgrade() -> None:
    op.drop_index("ix_node_lifecycle_states_current_run_id", table_name="node_lifecycle_states")
    op.drop_index("ix_node_lifecycle_states_run_status", table_name="node_lifecycle_states")
    op.drop_index("ix_node_lifecycle_states_lifecycle_state", table_name="node_lifecycle_states")
    op.drop_table("node_lifecycle_states")
