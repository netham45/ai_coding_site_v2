"""create yaml schema validation records table

Revision ID: 0004_yaml_schema_records
Revises: 0003_configurable_node_hierarchy
Create Date: 2026-03-08 01:05:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_yaml_schema_records"
down_revision = "0003_configurable_node_hierarchy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "yaml_schema_validation_records",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("source_group", sa.String(length=64), nullable=False),
        sa.Column("relative_path", sa.String(length=255), nullable=False),
        sa.Column("family", sa.String(length=64), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("issue_count", sa.Integer(), nullable=False),
        sa.Column("issues_json", sa.JSON(), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_yaml_schema_validation_records_source_group", "yaml_schema_validation_records", ["source_group"])
    op.create_index("ix_yaml_schema_validation_records_validated_at", "yaml_schema_validation_records", ["validated_at"])


def downgrade() -> None:
    op.drop_index("ix_yaml_schema_validation_records_validated_at", table_name="yaml_schema_validation_records")
    op.drop_index("ix_yaml_schema_validation_records_source_group", table_name="yaml_schema_validation_records")
    op.drop_table("yaml_schema_validation_records")
