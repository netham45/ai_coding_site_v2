"""create source document lineage tables

Revision ID: 0007_source_doc_lineage
Revises: 0006_node_version_supersession
Create Date: 2026-03-08 05:15:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_source_doc_lineage"
down_revision = "0006_node_version_supersession"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_documents",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("source_group", sa.String(length=64), nullable=False),
        sa.Column("relative_path", sa.String(length=255), nullable=False),
        sa.Column("doc_family", sa.String(length=64), nullable=False),
        sa.Column("source_role", sa.String(length=64), nullable=False),
        sa.Column("merge_mode", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_source_documents_source_group", "source_documents", ["source_group"])
    op.create_index("ix_source_documents_doc_family", "source_documents", ["doc_family"])
    op.create_index("ix_source_documents_source_role", "source_documents", ["source_role"])
    op.create_index("ix_source_documents_content_hash", "source_documents", ["content_hash"])

    op.create_table(
        "node_version_source_documents",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("source_document_id", sa.Uuid(), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("source_role", sa.String(length=64), nullable=False),
        sa.Column("resolution_order", sa.Integer(), nullable=False),
        sa.Column("is_resolved_input", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("node_version_id", "source_document_id", "source_role", name="uq_node_version_source_document_role"),
    )
    op.create_index("ix_node_version_source_documents_node_version_id", "node_version_source_documents", ["node_version_id"])
    op.create_index("ix_node_version_source_documents_source_document_id", "node_version_source_documents", ["source_document_id"])


def downgrade() -> None:
    op.drop_index("ix_node_version_source_documents_source_document_id", table_name="node_version_source_documents")
    op.drop_index("ix_node_version_source_documents_node_version_id", table_name="node_version_source_documents")
    op.drop_table("node_version_source_documents")
    op.drop_index("ix_source_documents_content_hash", table_name="source_documents")
    op.drop_index("ix_source_documents_source_role", table_name="source_documents")
    op.drop_index("ix_source_documents_doc_family", table_name="source_documents")
    op.drop_index("ix_source_documents_source_group", table_name="source_documents")
    op.drop_table("source_documents")
