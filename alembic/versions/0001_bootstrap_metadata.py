"""create bootstrap metadata table

Revision ID: 0001_bootstrap_metadata
Revises: 
Create Date: 2026-03-08 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_bootstrap_metadata"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bootstrap_metadata",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("schema_key", sa.String(length=100), nullable=False),
        sa.Column("schema_version", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("schema_key"),
    )
    op.execute(
        sa.text(
            """
            insert into bootstrap_metadata (id, schema_key, schema_version, notes)
            values (
                1,
                'database_bootstrap',
                '0001_bootstrap_metadata',
                'Initial database bootstrap revision for local and CI environment verification.'
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_table("bootstrap_metadata")
