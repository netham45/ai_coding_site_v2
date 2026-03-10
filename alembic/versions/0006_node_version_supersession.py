"""create node versioning and supersession tables

Revision ID: 0006_node_version_supersession
Revises: 0005_node_lifecycle_state
Create Date: 2026-03-08 04:20:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_node_version_supersession"
down_revision = "0005_node_lifecycle_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_versions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("logical_node_id", sa.Uuid(), sa.ForeignKey("hierarchy_nodes.node_id"), nullable=False),
        sa.Column("parent_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=True),
        sa.Column("tier", sa.String(length=32), nullable=False),
        sa.Column("node_kind", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("supersedes_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=True, unique=True),
        sa.Column("active_branch_name", sa.String(length=255), nullable=True),
        sa.Column("branch_generation_number", sa.Integer(), nullable=True),
        sa.Column("seed_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("final_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("version_number > 0", name="ck_node_versions_version_number_positive"),
        sa.CheckConstraint(
            "status in ('authoritative','candidate','failed_candidate','superseded')",
            name="ck_node_versions_status",
        ),
        sa.CheckConstraint(
            "supersedes_node_version_id is null or supersedes_node_version_id <> id",
            name="ck_node_versions_no_self_supersession",
        ),
        sa.UniqueConstraint("logical_node_id", "version_number", name="uq_node_versions_logical_node_version_number"),
    )
    op.create_index("ix_node_versions_logical_node_id", "node_versions", ["logical_node_id"])
    op.create_index("ix_node_versions_parent_node_version_id", "node_versions", ["parent_node_version_id"])
    op.create_index("ix_node_versions_node_kind", "node_versions", ["node_kind"])
    op.create_index("ix_node_versions_status", "node_versions", ["status"])
    op.create_index("ix_node_versions_active_branch_name", "node_versions", ["active_branch_name"])
    op.create_index("ix_node_versions_supersedes_node_version_id", "node_versions", ["supersedes_node_version_id"])

    op.create_table(
        "logical_node_current_versions",
        sa.Column("logical_node_id", sa.Uuid(), sa.ForeignKey("hierarchy_nodes.node_id"), primary_key=True, nullable=False),
        sa.Column("authoritative_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("latest_created_node_version_id", sa.Uuid(), sa.ForeignKey("node_versions.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_logical_node_current_versions_authoritative_node_version_id",
        "logical_node_current_versions",
        ["authoritative_node_version_id"],
    )
    op.create_index(
        "ix_logical_node_current_versions_latest_created_node_version_id",
        "logical_node_current_versions",
        ["latest_created_node_version_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_logical_node_current_versions_latest_created_node_version_id", table_name="logical_node_current_versions")
    op.drop_index("ix_logical_node_current_versions_authoritative_node_version_id", table_name="logical_node_current_versions")
    op.drop_table("logical_node_current_versions")
    op.drop_index("ix_node_versions_supersedes_node_version_id", table_name="node_versions")
    op.drop_index("ix_node_versions_active_branch_name", table_name="node_versions")
    op.drop_index("ix_node_versions_status", table_name="node_versions")
    op.drop_index("ix_node_versions_node_kind", table_name="node_versions")
    op.drop_index("ix_node_versions_parent_node_version_id", table_name="node_versions")
    op.drop_index("ix_node_versions_logical_node_id", table_name="node_versions")
    op.drop_table("node_versions")
