"""create validation results table

Revision ID: 0015_validation_results
Revises: 0014_rebuild_events
Create Date: 2026-03-08 13:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0015_validation_results"
down_revision = "0014_rebuild_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("compiled_subtask_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("check_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_validation_results_node_version_id"), "validation_results", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_validation_results_node_run_id"), "validation_results", ["node_run_id"], unique=False)
    op.create_index(op.f("ix_validation_results_compiled_subtask_id"), "validation_results", ["compiled_subtask_id"], unique=False)
    op.create_index(op.f("ix_validation_results_check_type"), "validation_results", ["check_type"], unique=False)
    op.create_index(op.f("ix_validation_results_status"), "validation_results", ["status"], unique=False)
    op.create_index(op.f("ix_validation_results_created_at"), "validation_results", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_validation_results_created_at"), table_name="validation_results")
    op.drop_index(op.f("ix_validation_results_status"), table_name="validation_results")
    op.drop_index(op.f("ix_validation_results_check_type"), table_name="validation_results")
    op.drop_index(op.f("ix_validation_results_compiled_subtask_id"), table_name="validation_results")
    op.drop_index(op.f("ix_validation_results_node_run_id"), table_name="validation_results")
    op.drop_index(op.f("ix_validation_results_node_version_id"), table_name="validation_results")
    op.drop_table("validation_results")
