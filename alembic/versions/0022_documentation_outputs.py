"""create documentation output history table

Revision ID: 0022_documentation_outputs
Revises: 0021_code_provenance_map
Create Date: 2026-03-09 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0022_documentation_outputs"
down_revision = "0021_code_provenance_map"
branch_labels = None
depends_on = None


DOC_SCOPES = ("local", "merged", "entity_history", "rationale_view", "custom")


def upgrade() -> None:
    op.create_table(
        "documentation_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("logical_node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doc_definition_id", sa.String(length=255), nullable=True),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("view_name", sa.String(length=64), nullable=False),
        sa.Column("output_path", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "scope in ('local','merged','entity_history','rationale_view','custom')",
            name="ck_documentation_outputs_scope",
        ),
        sa.ForeignKeyConstraint(["logical_node_id"], ["hierarchy_nodes.node_id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documentation_outputs_logical_node_id", "documentation_outputs", ["logical_node_id"])
    op.create_index("ix_documentation_outputs_node_version_id", "documentation_outputs", ["node_version_id"])
    op.create_index("ix_documentation_outputs_scope", "documentation_outputs", ["scope"])
    op.create_index("ix_documentation_outputs_view_name", "documentation_outputs", ["view_name"])
    op.create_index("ix_documentation_outputs_created_at", "documentation_outputs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_documentation_outputs_created_at", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_view_name", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_scope", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_node_version_id", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_logical_node_id", table_name="documentation_outputs")
    op.drop_table("documentation_outputs")
