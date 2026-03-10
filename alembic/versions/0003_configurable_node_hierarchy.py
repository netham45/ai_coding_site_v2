"""create configurable node hierarchy tables

Revision ID: 0003_configurable_node_hierarchy
Revises: 0002_daemon_authority_records
Create Date: 2026-03-08 00:40:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_configurable_node_hierarchy"
down_revision = "0002_daemon_authority_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_hierarchy_definitions",
        sa.Column("kind", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("tier", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("main_prompt", sa.String(length=255), nullable=False),
        sa.Column("entry_task", sa.String(length=100), nullable=False),
        sa.Column("available_tasks_json", sa.JSON(), nullable=False),
        sa.Column("allow_parentless", sa.Boolean(), nullable=False),
        sa.Column("allowed_parent_kinds_json", sa.JSON(), nullable=False),
        sa.Column("allowed_parent_tiers_json", sa.JSON(), nullable=False),
        sa.Column("allowed_child_kinds_json", sa.JSON(), nullable=False),
        sa.Column("allowed_child_tiers_json", sa.JSON(), nullable=False),
        sa.Column("min_children", sa.Integer(), nullable=True),
        sa.Column("max_children", sa.Integer(), nullable=True),
        sa.Column("source_path", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "hierarchy_nodes",
        sa.Column("node_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("parent_node_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=100), nullable=False),
        sa.Column("tier", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("created_via", sa.String(length=32), nullable=False),
        sa.Column("max_children", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_node_id"], ["hierarchy_nodes.node_id"]),
        sa.ForeignKeyConstraint(["kind"], ["node_hierarchy_definitions.kind"]),
        sa.CheckConstraint("created_via = 'daemon'", name="ck_hierarchy_nodes_created_via"),
    )
    op.create_index("ix_hierarchy_nodes_parent_node_id", "hierarchy_nodes", ["parent_node_id"])
    op.create_index("ix_hierarchy_nodes_kind", "hierarchy_nodes", ["kind"])


def downgrade() -> None:
    op.drop_index("ix_hierarchy_nodes_kind", table_name="hierarchy_nodes")
    op.drop_index("ix_hierarchy_nodes_parent_node_id", table_name="hierarchy_nodes")
    op.drop_table("hierarchy_nodes")
    op.drop_table("node_hierarchy_definitions")
