"""create review results table and mirror current review summary

Revision ID: 0016_review_results
Revises: 0015_validation_results
Create Date: 2026-03-08 15:10:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0016_review_results"
down_revision = "0015_validation_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subtask_attempts", sa.Column("review_json", sa.JSON(), nullable=True))
    op.create_table(
        "review_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("compiled_subtask_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("review_definition_id", sa.String(length=128), nullable=True),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("criteria_json", sa.JSON(), nullable=True),
        sa.Column("findings_json", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_results_node_version_id"), "review_results", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_review_results_node_run_id"), "review_results", ["node_run_id"], unique=False)
    op.create_index(op.f("ix_review_results_compiled_subtask_id"), "review_results", ["compiled_subtask_id"], unique=False)
    op.create_index(op.f("ix_review_results_review_definition_id"), "review_results", ["review_definition_id"], unique=False)
    op.create_index(op.f("ix_review_results_scope"), "review_results", ["scope"], unique=False)
    op.create_index(op.f("ix_review_results_status"), "review_results", ["status"], unique=False)
    op.create_index(op.f("ix_review_results_created_at"), "review_results", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_review_results_created_at"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_status"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_scope"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_review_definition_id"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_compiled_subtask_id"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_node_run_id"), table_name="review_results")
    op.drop_index(op.f("ix_review_results_node_version_id"), table_name="review_results")
    op.drop_table("review_results")
    op.drop_column("subtask_attempts", "review_json")
