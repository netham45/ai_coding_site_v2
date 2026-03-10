"""add runtime environment metadata

Revision ID: 0024_runtime_env_meta
Revises: 0023_action_automation
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0024_runtime_env_meta"
down_revision = "0023_action_automation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("compiled_subtasks", sa.Column("environment_policy_ref", sa.String(length=255), nullable=True))
    op.add_column("compiled_subtasks", sa.Column("environment_request_json", sa.JSON(), nullable=True))
    op.add_column("subtask_attempts", sa.Column("execution_environment_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("subtask_attempts", "execution_environment_json")
    op.drop_column("compiled_subtasks", "environment_request_json")
    op.drop_column("compiled_subtasks", "environment_policy_ref")
