"""create test results table and mirror current testing summary

Revision ID: 0017_test_results
Revises: 0016_review_results
Create Date: 2026-03-08 18:25:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0017_test_results"
down_revision = "0016_review_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subtask_attempts", sa.Column("testing_json", sa.JSON(), nullable=True))
    op.create_table(
        "test_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("compiled_subtask_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("testing_definition_id", sa.String(length=128), nullable=True),
        sa.Column("suite_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=True),
        sa.Column("results_json", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_results_node_version_id"), "test_results", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_test_results_node_run_id"), "test_results", ["node_run_id"], unique=False)
    op.create_index(op.f("ix_test_results_compiled_subtask_id"), "test_results", ["compiled_subtask_id"], unique=False)
    op.create_index(op.f("ix_test_results_testing_definition_id"), "test_results", ["testing_definition_id"], unique=False)
    op.create_index(op.f("ix_test_results_suite_name"), "test_results", ["suite_name"], unique=False)
    op.create_index(op.f("ix_test_results_status"), "test_results", ["status"], unique=False)
    op.create_index(op.f("ix_test_results_created_at"), "test_results", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_results_created_at"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_status"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_suite_name"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_testing_definition_id"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_compiled_subtask_id"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_node_run_id"), table_name="test_results")
    op.drop_index(op.f("ix_test_results_node_version_id"), table_name="test_results")
    op.drop_table("test_results")
    op.drop_column("subtask_attempts", "testing_json")
