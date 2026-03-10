"""create child materialization authority tables

Revision ID: 0012_child_materialization
Revises: 0011_session_binding_and_resume
Create Date: 2026-03-08 23:20:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0012_child_materialization"
down_revision = "0011_session_binding_and_resume"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_children",
        sa.Column("parent_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("child_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("layout_child_id", sa.String(length=128), nullable=False),
        sa.Column("origin_type", sa.String(length=32), nullable=False, server_default="layout_generated"),
        sa.Column("ordinal", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["parent_node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("parent_node_version_id", "child_node_version_id"),
        sa.CheckConstraint("parent_node_version_id <> child_node_version_id", name="ck_node_children_not_self"),
        sa.CheckConstraint(
            "origin_type in ('manual','layout_generated','layout_generated_then_modified')",
            name="ck_node_children_origin_type",
        ),
    )
    op.create_index("ix_node_children_origin_type", "node_children", ["origin_type"])
    op.create_index("ix_node_children_layout_child_id", "node_children", ["layout_child_id"])
    op.create_index("ix_node_children_child_node_version_id", "node_children", ["child_node_version_id"])
    op.create_index("ix_node_children_parent_ordinal", "node_children", ["parent_node_version_id", "ordinal"])

    op.create_table(
        "parent_child_authority",
        sa.Column("parent_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("authority_mode", sa.String(length=32), nullable=False, server_default="layout_authoritative"),
        sa.Column("authoritative_layout_hash", sa.String(length=64), nullable=True),
        sa.Column("last_reconciled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("parent_node_version_id"),
        sa.CheckConstraint(
            "authority_mode in ('manual','layout_authoritative','hybrid')",
            name="ck_parent_child_authority_mode",
        ),
    )
    op.create_index("ix_parent_child_authority_layout_hash", "parent_child_authority", ["authoritative_layout_hash"])


def downgrade() -> None:
    op.drop_index("ix_parent_child_authority_layout_hash", table_name="parent_child_authority")
    op.drop_table("parent_child_authority")
    op.drop_index("ix_node_children_parent_ordinal", table_name="node_children")
    op.drop_index("ix_node_children_child_node_version_id", table_name="node_children")
    op.drop_index("ix_node_children_layout_child_id", table_name="node_children")
    op.drop_index("ix_node_children_origin_type", table_name="node_children")
    op.drop_table("node_children")
