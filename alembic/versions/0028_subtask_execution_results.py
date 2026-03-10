"""add explicit subtask execution result payloads

Revision ID: 0028_subtask_execution_results
Revises: 0027_provenance_docs_audit_views
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0028_subtask_execution_results"
down_revision = "0027_provenance_docs_audit_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subtask_attempts", sa.Column("execution_result_json", sa.JSON(), nullable=True))
    op.create_index(
        "ix_subtask_attempts_run_subtask_created",
        "subtask_attempts",
        ["node_run_id", "compiled_subtask_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_subtask_attempts_run_subtask_created", table_name="subtask_attempts")
    op.drop_column("subtask_attempts", "execution_result_json")
